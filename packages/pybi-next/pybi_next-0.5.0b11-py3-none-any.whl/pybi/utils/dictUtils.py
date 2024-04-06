from typing import TYPE_CHECKING, List, Dict, Any
from itertools import chain


def _extract_path(path: str):
    """
    >>> _extract_path('series[0]')
    >>> ['series',0]

    >>> _extract_path('data')
    >>> ['data']
    """
    if path[-1] == "]":
        arr = path.split("[")
        yield arr[0]
        yield int(arr[1][:-1])
    else:
        yield path


def get_by_paths(paths: List[str], data: Dict):
    """
    >>> dict_data = {
        'series':[
            {
                'data':[1,2,3,4]
            }
        ]
    }
    >>> get_by_paths(['series[0]','data'],dict_data)
    >>> [1,2,3,4]
    """

    if len(paths) == 0:
        return data

    ex_paths = chain.from_iterable(_extract_path(p) for p in paths)

    target = data[next(ex_paths)]

    for path in ex_paths:
        target = target[path]

    return target


def set_by_paths(paths: List[str], data: Dict, value: Any):
    """
    >>> dict_data = {
        'series':[
            {
                'data':[1,2,3,4]
            }
        ]
    }
    >>> set_by_paths(['series[0]','data'],dict_data,'changed')
    >>> dict_data
    >>> {
        'series':[
            {
                'data':'changed'
            }
        ]
    }
    """

    if len(paths) == 0:
        return

    ex_paths = list(chain.from_iterable(_extract_path(p) for p in paths))

    if len(ex_paths) == 1:
        data[ex_paths[0]] = value
        return

    target = data[ex_paths[0]]

    for p in ex_paths[1:-1]:
        target = target[p]

    target[ex_paths[-1]] = value
