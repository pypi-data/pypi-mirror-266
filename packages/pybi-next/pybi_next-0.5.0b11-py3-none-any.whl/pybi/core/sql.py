from __future__ import annotations
from pybi.utils.data_gen import Jsonable
from typing import Optional, List

import re

m_sql_from_text_pat = re.compile(
    r"(?:info:\[\|sql:)(.+?)\|type:(.+?)\|js_map:(.*?)(?:\|])", re.I | re.DOTALL
)

m_foreach_text_pat = re.compile(r"(?:foreach:\[\|field:)(.+?)(?:\|])", re.I | re.DOTALL)


class SqlWrapper(Jsonable):
    def __init__(self, sql: str) -> None:
        super().__init__()
        self._sql_info = SqlInfo(sql)

    def split_group(self, by: str, code: str):
        code = f"""
function temp(key, rows, index){{
    {code}
}}
const gp = utils.groupBy(rows,'{by}')
const res =  Object.entries(gp).map(([key, rows], index) => temp(key,rows,index))
return res
        """
        return self.js_map(code)

    def js_map(self, code: str):
        """
        code: js code
            js vars:
                `rows` is object : query result rows,each row is object
                `fields` is string array : query result field names
                `utils` utils functions : `{uniq,groupBy}`
        ---
        pbi.sql(f"select name,age,value from {data}")
            `rows` e.g `[{name:'x1',age:20,value:100},{name:'x2',age:30,value:200},...]`
            `fields` e.g `['name','age','value']`
        """
        self._sql_info.jsMap = code
        self._sql_info.set_udf_type()
        return self

    def toflatlist(self, with_header=False):
        """
        >>> query = pbi.sql('select name,value from {data}')
        >>> query.toflatlist()
        >>> [
                ['name a',100],
                ['name b',200],
                ...
            ]

        >>> query.toflatlist(True)
        >>> [
                ['name','value'],
                ['name a',100],
                ['name b',200],
                ...
            ]
        """

        cols_define = "const cols=[fields]" if with_header else "const cols=[]"

        self.js_map(
            f"""
{cols_define}
if (fields.length>1){{
    return [...cols,...rows.map(data=> fields.map(f=> data[f]))] 
}}else {{
    return [...cols,...rows.map(data=>data[fields[0]])]
}}"""
        )
        return self

    def __str__(self) -> str:
        return str(self._sql_info)

    def _to_json_dict(self):
        return self._sql_info


class ForeachRowInfo(Jsonable):
    def __init__(self, field: str) -> None:
        super().__init__()
        self.field = field

    @staticmethod
    def extract_from_text(text: str):
        """
        >>> input = '字段名字:foreach:[|field:name|]'
        >>> extract_from_text(input)
        >>> ['字段名字:',ForeachRowInfo('name')]
        """
        start_idx = 0

        for match in re.finditer(m_foreach_text_pat, text):
            span = match.span()

            if span[0] > start_idx:
                # 前面有普通文本
                yield text[start_idx : span[0]]

            yield ForeachRowInfo(match.group(1))
            start_idx = span[1]

        end_idx = len(text) - 1

        if start_idx <= end_idx:
            yield text[start_idx : len(text)]

    def __str__(self) -> str:
        return f"foreach:[|field:{self.field}|]"


class SqlInfo(Jsonable):
    def __init__(
        self, sql: str, type: str = "infer", js_map: Optional[str] = None
    ) -> None:
        """
        type:
            'udf' : user defined function
            'infer' : automatically extrapolate from the results
        """
        super().__init__()
        self.sql = sql
        self.type = type
        self.jsMap = js_map

    def set_udf_type(self):
        self.type = "udf"
        return self

    def __str__(self) -> str:
        return f"info:[|sql:{self.sql}|type:{self.type}|js_map:{self.jsMap or ''}|]"

    @staticmethod
    def extract_sql_from_text(text: str):
        """
        >>> input = '总销售额:sql:[_ select sum(销售额) from data _]'
        >>> extract_sql_from_text(input)
        >>> ['总销售额:',Sql('select sum(销售额) from data')]
        """
        start_idx = 0

        for match in re.finditer(m_sql_from_text_pat, text):
            span = match.span()

            if span[0] > start_idx:
                # 前面有普通文本
                yield text[start_idx : span[0]]

            js_map = match.group(3)
            yield SqlInfo(
                match.group(1), match.group(2), None if len(js_map) == 0 else js_map
            )
            start_idx = span[1]

        end_idx = len(text) - 1

        if start_idx <= end_idx:
            yield text[start_idx : len(text)]

    @staticmethod
    def around_backticks(text: str):
        def add_backtick(match: re.Match):
            return f"`{match.group()}`"

        return m_sql_from_text_pat.sub(add_backtick, text)


def extract_sql_text(sql_text: str):
    for t in SqlInfo.extract_sql_from_text(sql_text):
        if isinstance(t, str):
            for t in ForeachRowInfo.extract_from_text(t):
                yield t

        else:
            yield t
