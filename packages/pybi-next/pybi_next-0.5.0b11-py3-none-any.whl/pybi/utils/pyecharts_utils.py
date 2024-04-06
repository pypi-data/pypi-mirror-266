from typing import TYPE_CHECKING, Dict, Sequence
import pybi.utils.echarts_opts_utils as echarts_opts_utils


def pyecharts_json_default(o, utils, basicOptsType):

    if isinstance(o, utils.JsCode):
        return (
            o.replace("\\n|\\t", "").replace(r"\\n", "\n").replace(r"\\t", "\t").js_code
        )
    if isinstance(o, basicOptsType):
        if isinstance(o.opts, Sequence):
            return [utils.remove_key_with_none_value(item) for item in o.opts]
        else:
            return utils.remove_key_with_none_value(o.opts)


def replace_jscode(options: Dict):
    from pyecharts.commons import utils as pyecharts_utils
    from pyecharts.options.series_options import BasicOpts

    iteror = echarts_opts_utils.iter_each_items(options)

    new_obj = None

    try:
        while 1:
            target, path = iteror.send(new_obj)
            new_obj = None
            if isinstance(target, pyecharts_utils.JsCode):
                code_str = (
                    target.replace("\\n|\\t", "")
                    .replace(r"\\n", "\n")
                    .replace(r"\\t", "\t")
                    .js_code
                )

                echarts_opts_utils.set_prop_by_path(options, path, code_str)

            if isinstance(target, BasicOpts):
                if isinstance(target.opts, Sequence):
                    new_obj = [
                        pyecharts_utils.remove_key_with_none_value(item)
                        for item in target.opts
                    ]
                    echarts_opts_utils.set_prop_by_path(options, path, new_obj)

                else:
                    new_obj = pyecharts_utils.remove_key_with_none_value(target.opts)
                    echarts_opts_utils.set_prop_by_path(options, path, new_obj)
    except StopIteration:
        pass

    # for target, path in iteror:
    #     if isinstance(target, pyecharts_utils.JsCode):
    #         code_str = (
    #             target.replace("\\n|\\t", "")
    #             .replace(r"\\n", "\n")
    #             .replace(r"\\t", "\t")
    #             .js_code
    #         )

    #         echarts_opts_utils.set_prop_by_path(options, path, code_str)

    #     if isinstance(target, BasicOpts):
    #         if isinstance(target.opts, Sequence):
    #             new_obj = [
    #                 pyecharts_utils.remove_key_with_none_value(item)
    #                 for item in target.opts
    #             ]
    #             echarts_opts_utils.set_prop_by_path(options, path, new_obj)
    #             iteror.send(new_obj)
    #         else:
    #             new_obj = pyecharts_utils.remove_key_with_none_value(target.opts)
    #             echarts_opts_utils.set_prop_by_path(options, path, new_obj)
    #             iteror.send(new_obj)

    return options
