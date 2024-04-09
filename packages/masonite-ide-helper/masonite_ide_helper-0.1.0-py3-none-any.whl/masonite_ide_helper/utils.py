import inspect
import re
from pathlib import Path
from pydoc import locate
from typing import Any
import os
from masoniteorm.query import QueryBuilder
from masoniteorm.scopes import scope

try:
    from config.database import DB, DATABASES
except ImportError:
    raise Exception("Cannot locate database config.")
from masonite_ide_helper.matchers import return_type_matcher, model_field_data_type_matcher


def to_class(path: str) -> Any:
    """
    Converts a string class path to a Python class.

    Args:
        path (str): The path of the class to be converted.

    Returns:
        Any: The Python class if found, otherwise None.
    """
    try:
        class_instance = locate(path)
    except ImportError:
        print('Module does not exist')
    return class_instance or None





def get_project_root(marker) -> str:
    """Get the root directory of the project."""
    # Start from the directory of the current script/module
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Traverse up until we find a known marker (e.g., a specific file)
    while not os.path.exists(os.path.join(current_dir, marker)):
        # Move one directory up
        current_dir = os.path.dirname(current_dir)
        # If we've reached the root directory, break the loop
        if current_dir == os.path.dirname(current_dir):
            break

    return current_dir


def extract_accessor_method(method_name):
    """
    Extracts the attribute name from a given method name.

    Args:
        method_name: The name of the method.

    Returns:
        str: The extracted attribute name.
    """
    result = re.search(r'get_(.*?)_attribute', method_name)
    if result:
        return result.group(1)
    else:
        return method_name


def get_method_parameters_as_string(method):
    """
    Retrieves the parameters of a given method as a string.

    Args:
        method: The method to retrieve parameters from.

    Returns:
        str: A string representation of the method parameters.
    """
    method_parameters = ""
    parameters = inspect.signature(method).parameters
    for param in parameters.items():
        param = param[1]
        if param.annotation and not isinstance(param, inspect._empty):
            method_parameters += f"{param}, "
        else:
            method_parameters += f"{param}, "
    return method_parameters.replace(": Self", "")


def get_passthrough_methods(cls):
    """
    Finds passthrough methods in a class.

    Args:
        cls: The class to inspect.

    Returns:
        dict: A dictionary containing passthrough methods along with their types and parameters.
    """
    methods_with_return_types = {}
    for method in cls.__passthrough__:
        if getattr(QueryBuilder, f"{method}", None):
            method_name = method
            method = getattr(QueryBuilder, method)
            methods_with_return_types[method_name] = {
                "type": return_type_matcher(inspect.signature(method).return_annotation),
                "params": get_method_parameters_as_string(method).rstrip(", ").replace("self, ", "")}
    return methods_with_return_types


def get_methods_with_return_types(cls):
    """
    Inspects a class and returns its methods along with their return types.

    Args:
        cls: The class to inspect.

    Returns:
        dict: A dictionary containing methods along with their return types and parameters.
    """
    default_methods = set(dir(object))
    methods_with_return_types = {}
    for name, method in inspect.getmembers(cls, inspect.isroutine):
        if name not in default_methods:
            return_type = Any
            try:
                method_parameters = get_method_parameters_as_string(method)
                return_type = return_type_matcher(inspect.signature(method).return_annotation)
                methods_with_return_types[name] = {"type": return_type, "params": method_parameters}

            except ValueError as e:
                if "relationships" in str(e):
                    return_type = return_type_matcher(inspect.signature(method.fn).return_annotation)
                    methods_with_return_types[name] = {"type": return_type, "import": return_type, "params": "self"}
            except AttributeError as e:
                continue
    return methods_with_return_types


def get_properties_with_annotations(cls):
    """
    Retrieves properties (attributes) of a class along with their types.

    Args:
        cls: The class to inspect.

    Returns:
        dict: A dictionary mapping property names to their types.
    """
    default_properties = [
        "__class__",
        "__doc__",
        "__module__",
        "__name__",
        "__bases__",
        "__qualname__",
        "__annotations__",
        "__dict__",
        "__weakref__"
    ]

    default_methods = [
        "__init__",
        "__str__",
        "__repr__",
        "__eq__",
        "__hash__"
        # Add more default methods as needed
    ]

    default_class_properties = default_properties + default_methods
    attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    properties = [a for a in attributes]
    return_types = {}
    properties_with_types = {}
    for prop_name, prop_value in properties:
        if not isinstance(prop_value, scope):
            return_types[prop_name] = type(prop_value)
    for prop_name, return_type in return_types.items():
        if prop_name not in default_class_properties:
            properties_with_types.update({
                prop_name: return_type.__name__
            })
    return properties_with_types


def get_model_fields_and_types(model: QueryBuilder):
    """
    Retrieves fields and their types from a model.

    Args:
        model (QueryBuilder): The model to inspect.

    Returns:
        dict: A dictionary mapping field names to their types.
    """
    DATABASES_: dict[str, Any] = DATABASES
    connection: str = model.__connection__
    connection_details: dict[str, Any] = DATABASES_[connection]
    if isinstance(connection_details, str):
        connection_details = DATABASES_[connection_details]
    driver: str = connection_details.get("driver")

    table: str = model.get_table_name()
    database: str = connection_details.get("database")
    results = []
    match driver:
        case "sqlite":
            results = DB.statement(
                f"""
                    PRAGMA table_info({table});
                """, connection=connection
            )
        case "mssql":
            results = DB.statement(
                f"""
                    SELECT column_name as name, data_type as type
                    FROM information_schema.columns
                    WHERE table_catalog = '{database}'
                    AND table_name = '{table}';
                """, connection=connection
            )
        case "mysql":
            results = DB.statement(
                f"""
                SELECT column_name as name, data_type as type
                FROM information_schema.columns
                WHERE table_schema = '{database}'
                AND table_name = '{table}';
                """, connection=connection
            )

    table_fields = {}
    if results:
        for field in results:
            name = field['name']
            return_type = model_field_data_type_matcher(field['type'])
            table_fields.update({
                name: return_type
            })
    return table_fields


def get_mutators_assessors(methods_with_types):
    """
    Identifies mutators (setters) and accessors (getters) from a list of methods with types.

    Args:
        methods_with_types (dict): A dictionary containing methods along with their return types.

    Returns:
        list: A list of mutators (setters).
    """
    mutators = []
    for field in methods_with_types:
        if extract_accessor_method(field) != field and extract_accessor_method(field) not in ['raw', 'dirty']:
            mutators.append(extract_accessor_method(field))
    return mutators
