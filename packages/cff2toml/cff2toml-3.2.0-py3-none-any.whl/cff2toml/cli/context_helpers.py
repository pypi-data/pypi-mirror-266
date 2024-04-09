from typing import Any
import typer


class TyperContextDictionary:

    _d: dict

    def __init__(self, ctx: typer.Context):
        if not isinstance(ctx.obj, dict):
            ctx.obj = dict()
        self._d = ctx.obj

    def has(self, key: str) -> bool:
        return key in self._d

    def get(self, key: str, default_value: Any = None):
        if key in self._d:
            return self._d[key]
        else:
            return default_value

    def set(self, key: str, value: Any):
        self._d[key] = value


def is_quiet_output(ctx: typer.Context):
    d = TyperContextDictionary(ctx=ctx)
    return d.get(key='quiet', default_value=False)


def is_verbose_output(ctx: typer.Context):
    d = TyperContextDictionary(ctx=ctx)
    return d.get(key='verbose', default_value=False)


def is_json_output(ctx: typer.Context):
    d = TyperContextDictionary(ctx=ctx)
    return d.get(key='json', default_value=False)
