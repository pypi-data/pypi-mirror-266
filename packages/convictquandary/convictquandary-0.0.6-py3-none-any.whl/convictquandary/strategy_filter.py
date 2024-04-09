import inspect

from . import strategies
from .strategy import Strategy


def strategy_filter(filters: dict[str, str]) -> list[Strategy]:
    all_classes = [
        obj
        for name, obj in inspect.getmembers(strategies)
        if inspect.isclass(obj) and not inspect.isabstract(obj) and hasattr(obj, "meta")
    ]
    filtered = [
        i
        for i in all_classes
        for k, v in filters.items()
        if k in i.meta.keys() and v in i.meta.values()
    ]
    return filtered
