# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _selecter.py
# @Time     : 2023/10/29 15:15
import re
from datetime import date, datetime
from re import Pattern
from typing import Optional, Type, Union, List, Any, Callable, Tuple, Dict

from fastapi import Depends, Query
from fastapi.exceptions import RequestValidationError
from sqlalchemy import desc
from sqlmodel import SQLModel
from typing_extensions import Annotated

from fastapix.common.pydantic import (
    model_fields, ModelField, Undefined,
    parse_date, parse_datetime,
    get_type_from_field,

)

sql_operator_pattern: Pattern = re.compile(r"^\[(=|<=|<|>|>=|!|!=|<>|\*|!\*|~|!~|-|\^|\$|#|\?|=\?|!\?|!=\?)]")
sql_operator_map: Dict[str, str] = {
    "=": "__eq__",
    "<=": "__le__",
    "<": "__lt__",
    ">": "__gt__",
    ">=": "__ge__",
    "!": "__ne__",
    "!=": "__ne__",
    "<>": "__ne__",
    "*": "in_",
    "!*": "not_in",
    "~": "like",
    "!~": "not_like",
    "-": "between",
    "^": "startswith",
    "$": "endswith",
    "#": "regexp_match",
    "?": "is_null",
    "=?": "is_null",
    "!?": "not_null",
    "!=?": "not_null"
}
sql_operator_docs = """
## 查询条件示例：
`[=]` : 等于, `abc` or `[=]abc`, 等于空字符串：`[=]`

`[!=]` : 不等, `[!]abc` or `[!=]abc`, 不等于空字符串：`[!]` or `[!=]`

`[=?]` : 空值查询, `[=?]` or `[?]`

`[!?]` : 非空查询, `[!?]` or `[!=?]`

`[~]` : 模糊查询, like, `[~]abc`

`[!~]` : 模糊查询, not like, `[!~]abc`

`[*]` : 在范围内, in, `[*]abc,def,gh`

`[!*]` : 不在范围内, not in, `[!*]abc,def,gh`

`[<]` : 小于, `[<]100`

`[<=]` : 小于等于, `[<=]100`

`[>]` : 大于, `[>]100`

`[>=]` : 大于等于, `[>=]100`

`[-]` : 范围查询, between, `[-]100,300`

`[^]` : 以...开头, `[^]abc`

`[$]` : 以...结尾, `[$]abc`

`[#]` : 正则查询, `[#]regex`

## 排序

`+` : 正序, `create_time` or `+create_time`

`-` : 倒序, `-create_time`

`,` : 多字段, `create_time,-id`
"""


def get_modelfield_by_alias(table_model: Type[SQLModel], alias: str) -> Optional[ModelField]:
    fields = model_fields(table_model).values()
    for field in fields:
        if field.alias == alias or getattr(fields, 'serialization_alias', None) == alias:
            return field
    return None


def required_parser_str_set_list(primary_key: Union[int, str]) -> List[str]:
    if isinstance(primary_key, int):
        return [str(primary_key)]
    elif not isinstance(primary_key, str):
        return []
    return list(set(primary_key.split(",")))


RequiredPrimaryKeyListDepend = Annotated[List[str], Depends(required_parser_str_set_list)]


def parser_ob_str_set_list(order_by: Optional[str] = None) -> List[str]:
    return required_parser_str_set_list(order_by)


OrderByListDepend = Annotated[List[str], Depends(parser_ob_str_set_list)]

VisibleFieldsListDepend = Annotated[List[str], Depends(parser_ob_str_set_list)]


def get_python_type_parse(field: ModelField) -> Callable:
    try:
        python_type = get_type_from_field(field)
        if issubclass(python_type, date):
            if issubclass(python_type, datetime):
                return parse_datetime
            return parse_date
        # todo(zhangzhanqi) 暂不支持 list dict 查询
        if issubclass(python_type, list):
            return str
        if isinstance(python_type, dict):
            return str
        return python_type
    except NotImplementedError:
        return str


class Selector:
    Model: Type[SQLModel]

    def __call__(self, *args, **kwargs):
        pass

    @staticmethod
    def _parser_query_value(
            value: Any, operator: str = "__eq__", python_type_parse: Callable = str
    ) -> Tuple[Optional[str], Union[tuple, None]]:
        if isinstance(value, str):
            if not value:
                return None, None
            match = sql_operator_pattern.match(value)
            if match:
                op_key = match.group(1)
                operator = sql_operator_map.get(op_key)
                value = value.replace(f"[{op_key}]", "")
                if not value:
                    if operator == "is_null":
                        return "is_", (None,)
                    elif operator == "not_null":
                        return "is_not", (None,)
                if operator in ["like", "not_like"] and value.find("%") == -1:
                    return operator, (f"%{value}%",)
                elif operator in ["in_", "not_in"]:
                    return operator, (list(map(python_type_parse, set(value.split(",")))),)
                elif operator == "between":
                    value = value.split(",")[:2]
                    if len(value) < 2:
                        return None, None
                    return operator, tuple(map(python_type_parse, value))
        return operator, (python_type_parse(value),)

    def calc_filter_clause(self):
        query = []
        errors = []
        for name, value in self.__dict__.items():
            sqlfield = model_fields(self.Model).get(name, None)
            if value:
                try:
                    operator, val = self._parser_query_value(value, python_type_parse=get_python_type_parse(sqlfield))
                    if operator:
                        query.append(getattr(getattr(self.Model, name), operator)(*val))
                except ValueError as e:
                    errors.append(
                        {
                            "type": "type_error",
                            "loc": ("query", name),
                            "msg": "JSON decode error",
                            "input": f"Input should be a valid {get_type_from_field(sqlfield)}, invalid {value}",
                            "ctx": {"error": e},
                        }
                    )
        if errors:
            raise RequestValidationError(errors)
        return query


class Paginator:
    def __init__(
            self,
            page: int = 1,
            page_size: int = None,
            show_total: bool = True,
            order_by: OrderByListDepend = None,
    ):
        self.page = page
        self.page_size = page_size
        self.show_total = show_total
        self.order_by = order_by

    def calc_ordering(self):
        order = []
        for ob in self.order_by:
            if isinstance(ob, str) and ob.startswith("-"):
                order.append(desc(ob[1:]))
            elif isinstance(ob, str) and ob.startswith("+"):
                order.append(ob[1:])
            else:
                order.append(ob)

        return order


def sqlmodel_to_selector(
        base_model: Type[SQLModel],
) -> Type[Selector]:
    imports = ['from fastapi import Query']
    params = []
    methods = []
    for name, field in model_fields(base_model).items():
        field_info = field.field_info
        if getattr(field_info, 'query', False) is False:
            continue
        if getattr(field_info, 'primary_key', False) is True:
            params.append(f"{name}: str = Query(None, alias='primary_key', "
                          f"description='`{base_model.__name__}.{name}`: 主键')")
            methods.append(f"self.{name} = {name}")
        else:
            params.append(
                f"""{name}: str = Query(None,
                    gt={getattr(field_info, 'gt', None)},
                    ge={getattr(field_info, 'ge', None)},
                    lt={getattr(field_info, 'lt', None)},
                    le={getattr(field_info, 'le', None)},
                    min_length={getattr(field_info, 'min_length', None)},
                    max_length={getattr(field_info, 'max_length', None)},
                    max_digits={getattr(field_info, 'max_digits', Undefined)},
                    decimal_places={getattr(field_info, 'decimal_places', Undefined)},
                  description="`{base_model.__name__}.{name}`: {field_info.title}")"""
            )
            methods.append(f"self.{name} = {name}")
    func = f"""
{";".join(set(imports))}
def call(
    self,
    {",".join(set(params))}
):
    {";".join(set(methods))}
    return self
    """
    exec(func, globals())

    return type(
        f'{base_model.__name__}Selector',
        (Selector,),
        {
            'Model': base_model,
            '__call__': call  # type: ignore
        }
    )
