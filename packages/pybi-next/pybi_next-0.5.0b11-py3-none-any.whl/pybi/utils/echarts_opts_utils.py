from typing import Any, Dict


def set_prop_by_path(options: Dict, path: str, value: Any):
    """
    path: 'sreies[0].data[0].item.value'
    """
    paths = [p for p in path.split(".") if len(p) > 0]
    target = options
    for path in paths[:-1]:
        if path[-1] == "]":
            # e.g sreies[0]
            start_idx = path.index("[")
            key = path[:start_idx]
            path_idx = int(path[start_idx + 1 : -1])
            target = target[key][path_idx]
        else:
            # e.g .item
            if path not in target:
                target[path] = {}
            target = target[path]

    path = paths[-1]
    if path[-1] == "]":
        # e.g sreies[0]
        start_idx = path.index("[")
        key = path[:start_idx]
        path_idx = int(path[start_idx + 1 : -1])
        target[key][path_idx] = value
    else:
        # e.g .item
        target[path] = value


def iter_each_items(options: Dict):
    """
    >>> opts = {'series':[{'type':'bar',data:[1,2]}]}
    >>> target,path = next(iter_each_items(opts))
    >>> target,path
    >>> [{'type':'bar',data:[1,2]}] , '.series'
    >>> {'type':'bar',data:[1,2]} , '.series[0]'
    """
    stack = [(options, "")]

    def interception_type(target, path):
        if isinstance(target, dict):
            inputs = ((value, f"{path}.{key}") for key, value in target.items())
            stack.extend(inputs)
            return True

        if isinstance(target, list):
            inputs = ((value, f"{path}[{idx}]") for idx, value in enumerate(target))
            stack.extend(inputs)
            return True

        return False

    while len(stack) > 0:
        target, path = stack.pop()

        if interception_type(target, path):
            continue

        resend = yield target, path
        if resend is not None:
            interception_type(resend, path)
