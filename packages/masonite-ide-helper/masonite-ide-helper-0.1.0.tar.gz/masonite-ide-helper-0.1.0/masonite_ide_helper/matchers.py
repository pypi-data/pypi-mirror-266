import datetime
import inspect
from typing import Callable

from masoniteorm.collection import Collection
from masoniteorm.query import QueryBuilder
from masoniteorm.scopes import scope


def model_field_data_type_matcher(return_type):
    if "int" in return_type.lower():
        return_type = "int"
    if "float" in return_type.lower() or "double" in return_type.lower() or "real" in return_type.lower():
        return_type = "float"
    if "decimal" in return_type.lower() or "numeric" in return_type.lower():
        return_type = "Decimal.Decimal"
    if "text" in return_type.lower() or "char" in return_type.lower():
        return_type = "str"
    if "date" in return_type.lower() or "time" in return_type.lower() or "interval" in return_type.lower():
        return_type = "datetime.datetime"
    if "bool" in return_type.lower():
        return_type = "bool"
    if "bool" in return_type.lower():
        return_type = "bool"
    return return_type


def return_type_matcher(return_type):
    if return_type is inspect._empty:
        return "Self"
    if return_type is str:
        return "str"
    if return_type is QueryBuilder:
        return "QueryBuilder"
    if return_type is int:
        return "int"
    if return_type is bool:
        return "bool"
    if return_type is datetime.datetime:
        return "datetime.datetime"
    if return_type is list:
        return "typing.List"
    if return_type is dict:
        return "typing.Dict"
    if return_type is set:
        return "typing.Set"
    if return_type is Callable:
        return "Callable"
    if return_type is Collection:
        return "Collection"
    if return_type is scope:
        return "QueryBuilder"
    return return_type
