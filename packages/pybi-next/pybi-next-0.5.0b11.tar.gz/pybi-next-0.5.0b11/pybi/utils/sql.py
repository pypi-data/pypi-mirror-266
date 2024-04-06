import re

s_sql_table_name_pat = re.compile(r"(?<=from|join)\s+(\w+\b)", re.I | re.DOTALL)
s_sql_fields_head_select_pat = re.compile(
    r"(?<=select)\s+?(.+?)\s+from", re.I | re.DOTALL
)


def extract_table_names(sql: str):
    return s_sql_table_name_pat.findall(sql.strip())


def extract_fields_head_select(sql: str):
    """
    >>> extract_fields_head_select('select a as name1,b,c from (select x from tab1)')
    >>> ['name1','b','c']
    """
    res = s_sql_fields_head_select_pat.findall(sql.strip())

    each_field_has_as = (f.strip().split(" as ") for f in _iter_name(res[0]))

    each_field = (f[0] if len(f) == 1 else f[-1] for f in each_field_has_as)
    each_field = (f.strip() for f in each_field)

    return list(each_field)


def _iter_name(text: str):

    brackets_num = 0
    start_idx = 0

    for cur_idx, letter in enumerate(text):
        if letter == "," and brackets_num == 0:
            yield text[start_idx:cur_idx]
            start_idx = cur_idx + 1
        elif letter == "(":
            brackets_num += 1
        elif letter == ")":
            brackets_num -= 1

    if start_idx <= len(text) - 1:
        yield text[start_idx : len(text)]

def apply_agg(self_agg: str, self_y: str):

    if '${}' in self_agg:
        return self_agg.replace('${}', self_y)
    else:
        return f'{self_agg}(`{self_y}`)'