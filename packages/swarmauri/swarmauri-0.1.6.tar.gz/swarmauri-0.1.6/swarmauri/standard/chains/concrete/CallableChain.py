from typing import Any, Callable, List, Dict
from swarmauri.core.chains.ICallableChain import ICallableChain, CallableDefinition

class CallableChain(ICallableChain):
    def __init__(self, callables: List[CallableDefinition] = None):
        self.callables = callables if callables is not None else []

    def __call__(self, *initial_args: Any, **initial_kwargs: Any) -> Any:
        result = None
        for func, args, kwargs in self.callables:
            # For the first callable, if initial_args or initial_kwargs are provided, use them
            if result is None and (initial_args or initial_kwargs):
                result = func(*initial_args, **initial_kwargs)
            else:
                args = [result] + list(args)
                result = func(*args, **kwargs)
        return result

    def add_callable(self, func: Callable[[Any], Any], args: List[Any] = None, kwargs: Dict[str, Any] = None) -> None:
        # Add a new callable to the chain
        self.callables.append((func, args or [], kwargs or {}))