import pandas as pd
from typing import Any, Callable, TypeVar, List, Iterable, Generator, Union

T = TypeVar("T")


def flatten(
    obj: T, children_fn: Callable[[T], Iterable[T]]
) -> Generator[T, None, None]:
    stack = [obj]

    while 1:
        if len(stack) <= 0:
            break
        target = stack.pop()
        yield target
        children = children_fn(target)
        for child in children:
            stack.append(child)


def df_na2none(df: pd.DataFrame):
    return df.where(pd.notnull(df), None)


def df2object_dict(df: pd.DataFrame):
    return df_na2none(df).to_dict("records")


def df2array_dict(df: pd.DataFrame):
    return df_na2none(df).values.tolist()


def value2code(v: Any):
    if v is None:
        return "null"
    return str(v) if not isinstance(v, str) else f"'{v}'"


def style_text2dict(style: str):
    pairs = style.split(";")
    items = (s.split(":") for s in pairs if s)
    items = (item for item in items if len(item) == 2)
    items = {name.strip(): value.strip() for name, value in items}
    return items
