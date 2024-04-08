#! -*- encoding: utf-8 -*-

# We import command modules inside their respective function bodies
# for performance reasons, so turn off the lint warning
# pylint: disable=import-outside-toplevel

import os
import sys
from functools import wraps
from typing import Optional

import click
import pkg_resources
import requests
from autoupgrade import Package
from click.exceptions import ClickException

from suite_py.__version__ import __version__
from suite_py.commands.context import Context
from suite_py.lib import logger, metrics
from suite_py.lib.config import Config
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.okta_handler import Okta
from suite_py.lib.tokens import Tokens

ALLOW_NO_GIT_SUBCOMMAND = ["login", "aggregator"]
ALLOW_NO_HOME_SUBCOMMAND = ["login", "aggregator"]


def maybe_inject_truststore() -> None:
    """
    Injects the truststore package into the system ssl store, to fix verficiation certificate issues when using warp.
    """
    if sys.version_info >= (3, 10):
        import truststore

        truststore.inject_into_ssl()
    else:
        logger.warning(
            "Your python version is older than 3.10 and doesn't support the truststore package. You might experience issues with certificate verification when connected to the warp VPN.\nPlease update to python 3.10 or newer"
        )


def fetch_latest_version() -> Optional[pkg_resources.packaging.version.Version]:
    """
    Fetches the latest version of suite-py as a pkg_resources parsed version
    Returns None on error
    """
    try:
        # pylint: disable-next=missing-timeout
        pkg_info = requests.get("https://pypi.org/pypi/suite-py/json").json()
        return pkg_resources.parse_version(pkg_info["info"]["version"])
    except Exception:
        logger.warning("Failed to fetch latest version of suite-py!")
        return None


def upgrade_suite_py_if_needed(break_on_missing_package: bool = False) -> None:
    """
    Sometimes, when `suite-py` is launched with a virtual environment active, autoupgrade
    cannot see the package as installed (as the command is used from the "global" user environment)
    and raises an exception.
    """

    try:
        pkg_resources.get_distribution("suite_py")
    except pkg_resources.DistributionNotFound as error:
        # We are in a virtual environment where suite-py is not installed, don't bother trying to upgrade
        if break_on_missing_package:
            raise error

        logger.warning(
            "Skipping Suite-Py autoupgrade because the package was not found in the current environment."
        )
        return

    current_version = pkg_resources.parse_version(__version__)

    try:
        # If available, upgrade (if needed)
        latest_version = fetch_latest_version()
        if latest_version is None or latest_version > current_version:
            # If we fail to fetch the latest version, fallback to attempting the upgrade anyway
            Package("suite_py").upgrade()
    except Exception as error:
        logger.warning(f"An error occurred whilst trying to upgrade suite-py: {error}")


# Catches any exceptions thrown and turns them into a ClickException
# So they don't print a stacktrace
def catch_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ClickException as e:
            raise e
        except Exception as e:
            logger.debug("An error occured:", exc_info=True)
            raise ClickException(f"{str(e)}. rerun with -v for more details") from e

    return wrapper


@click.group()
@click.option(
    "--project",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path of the project to run the command on (the default is current directory)",
)
@click.option(
    "--timeout",
    type=click.INT,
    help="Timeout in seconds for Captainhook operations",
)
@click.option("-v", "--verbose", count=True)
@click.pass_context
@catch_exceptions
def main(ctx, project, timeout, verbose):
    config = Config()

    logger.setup(verbose)

    logger.debug(f"v{__version__}")
    maybe_inject_truststore()
    upgrade_suite_py_if_needed(break_on_missing_package=False)

    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND:
        project = git.get_root_folder(project)

    if ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND and not git.is_repo(
        project
    ):
        raise Exception(f"the folder {project} is not a git repo")

    if ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND and not os.path.basename(
        project
    ) in os.listdir(config.user["projects_home"]):
        raise Exception(
            f"the folder {project} is not in {config.user['projects_home']}"
        )

    skip_confirmation = False
    if type(config.user.get("skip_confirmation")).__name__ == "bool":
        skip_confirmation = config.user.get("skip_confirmation")
    elif type(
        config.user.get("skip_confirmation")
    ).__name__ == "list" and ctx.invoked_subcommand in config.user.get(
        "skip_confirmation"
    ):
        skip_confirmation = True

    if not skip_confirmation and not prompt_utils.ask_confirm(
        f"Do you want to continue on project {os.path.basename(project)}?"
    ):
        return
    if timeout:
        config.user["captainhook_timeout"] = timeout

    project = os.path.basename(project)
    tokens = Tokens()
    okta = Okta(config, tokens)
    captainhook = CaptainHook(config, okta, tokens)

    ctx.obj = Context(
        project=project,
        tokens=tokens,
        okta=okta,
        config=config,
        captainhook=captainhook,
    )

    ctx.obj.call(metrics.setup)

    # Skip chdir if not needed
    if (
        ctx.invoked_subcommand not in ALLOW_NO_GIT_SUBCOMMAND
        or ctx.invoked_subcommand not in ALLOW_NO_HOME_SUBCOMMAND
    ):
        os.chdir(os.path.join(config.user["projects_home"], ctx.obj.project))


@main.result_callback()
@click.pass_obj
def cleanup(_obj, _, **_kwargs):
    metrics.async_upload()


@main.command("bump", help="Bumps the project version based on the .versions.yml file")
@click.option("--project", required=False, type=str)
@click.option(
    "--version",
    required=False,
    type=str,
    help="Version to apply. If not passed, you will be prompted to insert or select one from a predefined list",
)
@click.pass_obj
@catch_exceptions
def bump(obj: Context, project: Optional[str] = None, version: Optional[str] = None):
    from suite_py.commands.bump import Bump

    obj.call(Bump).run(project=project, version=version)


@main.command(
    "create-branch", help="Create local branch and set the YouTrack card in progress"
)
@click.option("--card", type=click.STRING, help="YouTrack card number (ex. PRIMA-123)")
@click.pass_obj
@catch_exceptions
def cli_create_branch(obj, card):
    from suite_py.commands.create_branch import CreateBranch

    obj.call(CreateBranch, card=card).run()


@main.command("lock", help="Lock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
@catch_exceptions
def cli_lock_project(obj, environment):
    from suite_py.commands.project_lock import ProjectLock

    obj.call(ProjectLock, env=environment, action="lock").run()


@main.command("unlock", help="Unlock project on staging or prod")
@click.argument(
    "environment", type=click.Choice(("staging", "production", "deploy", "merge"))
)
@click.pass_obj
@catch_exceptions
def cli_unlock_project(obj, environment):
    from suite_py.commands.project_lock import ProjectLock

    obj.call(ProjectLock, env=environment, action="unlock").run()


@main.command("open-pr", help="Open a PR on GitHub")
@click.pass_obj
@catch_exceptions
def cli_open_pr(obj):
    from suite_py.commands.open_pr import OpenPR
    from suite_py.commands.ask_review import AskReview

    ask_review = obj.call(AskReview)
    obj.call(OpenPR, ask_review=ask_review).run()


@main.command("ask-review", help="Requests a PR review")
@click.pass_obj
@catch_exceptions
def cli_ask_review(obj):
    from suite_py.commands.ask_review import AskReview

    obj.call(AskReview).run()


@main.command(
    "merge-pr", help="Merge the selected branch to master if all checks are OK"
)
@click.pass_obj
@catch_exceptions
def cli_merge_pr(obj):
    from suite_py.commands.merge_pr import MergePR

    obj.call(MergePR).run()


@main.group("release", help="Manage releases")
def release():
    pass


@release.command(
    "create", help="Create a github release (and deploy it if GHA are used)"
)
@click.option(
    "--deploy",
    is_flag=True,
    help="Trigger deploy with Drone CI after release creation (Github Actions based microservices will be automatically deployed on production)",
)
@click.pass_obj
@catch_exceptions
def cli_release_create(obj, deploy):
    from suite_py.commands.release import Release

    obj.call(Release, action="create", flags={"deploy": deploy}).run()


@release.command("deploy", help="Deploy a github release with Drone CI")
@click.pass_obj
@catch_exceptions
def cli_release_deploy(obj):
    from suite_py.commands.release import Release

    obj.call(Release, action="deploy").run()


@release.command("rollback", help="Rollback a deployment")
@click.pass_obj
@catch_exceptions
def cli_release_rollback(obj):
    from suite_py.commands.release import Release

    obj.call(Release, "rollback").run()


@main.command("deploy", help="Deploy master branch in production")
@click.pass_obj
@catch_exceptions
def cli_deploy(obj):
    from suite_py.commands.deploy import Deploy

    obj.call(Deploy).run()


@main.group("docker", help="Manage docker images")
def docker():
    pass


@docker.command("release", help="Release new docker image")
@click.pass_obj
@catch_exceptions
def cli_docker_release(obj):
    from suite_py.commands.docker import Docker

    obj.call(Docker, action="release").run()


@docker.command("versions", help="List all available versions of specific image")
@click.pass_obj
@catch_exceptions
def cli_docker_versions(obj):
    from suite_py.commands.docker import Docker

    obj.call(Docker, action="versions").run()


@main.command("status", help="Current status of a project")
@click.pass_obj
@catch_exceptions
def cli_status(obj):
    from suite_py.commands.status import Status

    obj.call(Status, action="versions").run()


@main.command("check", help="Verify authorisations for third party services")
@click.pass_obj
@catch_exceptions
def cli_check(obj):
    from suite_py.commands.check import Check

    obj.call(Check).run()


@main.command("id", help="Get the ID of the hosts where the task is running")
@click.argument("environment", type=click.Choice(("staging", "production")))
@click.pass_obj
@catch_exceptions
def cli_id(obj, environment):
    from suite_py.commands.id import ID

    obj.call(ID, environment=environment).run()


@main.command("ip", help="Get the IP addresses of the hosts where the task is running")
@click.argument("environment", type=click.Choice(("staging", "production")))
@click.pass_obj
@catch_exceptions
def cli_ip(obj, environment):
    from suite_py.commands.ip import IP

    obj.call(IP, environment=environment).run()


@main.command("generator", help="Generate different files from templates")
@click.pass_obj
@catch_exceptions
def cli_generator(obj):
    from suite_py.commands.generator import Generator

    obj.call(Generator).run()


@main.group(
    "aggregator",
    help="Manage CNAMEs of aggregators in QA envs",
    invoke_without_command=True,
)
@click.option(
    "-l", "--list", "show_list", help="deprecated", required=False, count=True
)
@click.option("-c", "--change", "change", help="deprecated", required=False, count=True)
@click.pass_context
def aggregator(ctx, show_list, change):
    if show_list == 1 or change == 1:
        logger.error(
            "suite-py aggregator [-c|-l] has been hard-deprecated. Use suite-py aggregator [list|change] instead."
        )
        sys.exit(0)

    if ctx.invoked_subcommand is None:
        logger.error("Missing command. Try suite-py aggregator --help for help.")
        sys.exit(0)


@aggregator.command("list", help="List all aggregators with the current record")
@click.pass_obj
@catch_exceptions
def cli_aggregator_list(obj):
    from suite_py.commands.aggregator import Aggregator

    obj.call(Aggregator, action="list").run()


@aggregator.command("change", help="Change aggregator record")
@click.pass_obj
@catch_exceptions
def cli_aggregator_change(obj):
    from suite_py.commands.aggregator import Aggregator

    obj.call(Aggregator, action="list").run()


@main.command("login", help="manage login against Auth0")
@click.pass_obj
@catch_exceptions
def login(obj):
    from suite_py.commands.login import Login

    obj.call(Login).run()


@main.group(
    "secret", help="Manage secrets grants in multiple countries (aws-vault needed)"
)
def secret():
    pass


@secret.command("create", help="Create a new secret")
@click.option("-b", "--base-profile", "base_profile", required=False)
@click.option("-f", "--secret-file", "secret_file", required=False)
@click.pass_obj
@catch_exceptions
def cli_secret_create(obj, base_profile, secret_file):
    from suite_py.commands.secret import Secret

    obj.call(
        Secret, action="create", base_profile=base_profile, secret_file=secret_file
    ).run()


@secret.command("grant", help="Grant permissions to an existing secret")
@click.option("-b", "--base-profile", "base_profile", required=False)
@click.option("-f", "--secret-file", "secret_file", required=False)
@click.pass_obj
@catch_exceptions
def cli_secret_grant(obj, base_profile, secret_file):
    from suite_py.commands.secret import Secret

    obj.call(
        Secret, action="grant", base_profile=base_profile, secret_file=secret_file
    ).run()


@main.command("batch-job", help="Run batch job on kube")
@click.argument("environment", type=click.Choice(("staging", "production")))
@click.option(
    "-c",
    "--cpu",
    "cpu_request",
    required=True,
    type=str,
    help="Millicpu format. E.g: 1000m (=1CPU)",
)
@click.option(
    "-m",
    "--memory",
    "memory_request",
    required=True,
    type=str,
    help="Mebibytes or gibibyte format. E.g: 256Mi or 1Gi",
)
@click.pass_obj
@catch_exceptions
def cli_run_batch_job(obj, environment, cpu_request, memory_request):
    from suite_py.commands.batch_job import BatchJob

    obj.call(
        BatchJob,
        environment=environment,
        cpu_request=cpu_request,
        memory_request=memory_request,
    ).run()


@main.command("set-token", help="Create or update a service token")
@click.pass_obj
@catch_exceptions
def cli_set_token(obj):
    from suite_py.commands.set_token import SetToken

    obj.call(SetToken).run()
