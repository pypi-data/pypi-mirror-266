import dataclasses
from inspect import signature

from suite_py.lib.config import Config
from suite_py.lib.handler.captainhook_handler import CaptainHook
from suite_py.lib.handler.okta_handler import Okta
from suite_py.lib.tokens import Tokens


@dataclasses.dataclass
class Context:
    project: str
    config: Config
    captainhook: CaptainHook
    tokens: Tokens
    okta: Okta

    # Call the function to_call with kwargs, injecting fields from self as default arguments
    def call(self, to_call, **kwargs):
        provided = dataclasses.asdict(self)
        needed = signature(to_call).parameters.keys()
        provided = {k: provided[k] for k in needed if k in provided}

        kwargs = provided | kwargs

        return to_call(**kwargs)
