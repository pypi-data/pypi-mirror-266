from typing import Any, Dict, List
from typing import Tuple

from masonite_ide_helper.utils import get_model_fields_and_types, get_mutators_assessors, extract_accessor_method


def generate_stub_data(model_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Generate structured data from model_data.

    Args:
        model_data (dict): Data about the model including name, class_name, properties, and methods.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]: Structured data including fields, properties, accessors, methods, relationships, and dynamic "where" clauses.
    """
    model_name = model_data["name"]
    class_name = model_data["class_name"]
    model_fields = get_model_fields_and_types(class_name)
    properties_with_types = model_data["properties"][0]
    methods_with_types = model_data["methods"][0]

    model_fields_with_relationships_removed = {}
    model_custom_accessors_with_types = {}
    relationships = []
    dynamic_wheres = {}

    # Process model fields
    for field, field_type in model_fields.items():
        if field not in methods_with_types:
            model_fields_with_relationships_removed[field] = field_type

    # Generate custom accessors
    for field in get_mutators_assessors(methods_with_types):
        if f"get_{field}_attribute" in methods_with_types:
            model_custom_accessors_with_types[extract_accessor_method(field)] = methods_with_types[f"get_{field}_attribute"]["type"]
            del methods_with_types[f"get_{field}_attribute"]

    # Sanitize Fields
    model_fields_with_relationships_removed = {field: field_type for field, field_type in model_fields_with_relationships_removed.items() if "-" not in field}

    # Get Dynamic Wheres
    dynamic_wheres = {f"where_{field}": "QueryBuilder" for field in model_fields_with_relationships_removed if "-" not in field}

    # Get Relationships from methods
    for method_name, return_type in methods_with_types.items():
        if return_type.get("import"):
            relationship = {"name": method_name, **return_type}
            relationships.append(relationship)

    # Get dynamic_wheres from methods
    for method_name, return_type in methods_with_types.items():
        if not isinstance(return_type, dict) and method_name.startswith("where_"):
            dynamic_wheres[method_name] = return_type

    # Remove processed methods
    methods_with_types = {method: return_type for method, return_type in methods_with_types.items() if method not in dynamic_wheres}

    return (
        model_fields_with_relationships_removed,
        properties_with_types,
        model_custom_accessors_with_types,
        methods_with_types,
        relationships,
        dynamic_wheres
    )


def generate_pyi_content(model_data, models_dir):
    """
    Generate a Python stub (.pyi) file based on model data.

    Args:
    - model_data (dict): A dictionary containing model information.
    - models_dir (str): The directory to save the generated .pyi file.

    Returns:
    - None
    """

    fields, properties, accessors, methods, relationships, dynamic_wheres = generate_stub_data(model_data)
    model_name = model_data.get("name")
    imports = []

    pyi_content = f"""
import typing\n
from typing import List, Dict, Self, Any, Set, Callable\n
import datetime\n
import masoniteorm\n
from masoniteorm.query import QueryBuilder\n
from masoniteorm.models import Model\n
from masoniteorm.collection.Collection import Collection\n\n

class {model_name}(Model):
        """
    # Add model fields from database
    pyi_content = pyi_content + "\n\n    # Model fields from database."
    for field_name, field_type in fields.items():
        pyi_content += f"\n    {field_name}: {field_type}"

    # Add properties from model
    pyi_content = pyi_content + "\n\n    # Properties from model."
    for property_name, property_type in properties.items():
        pyi_content += f"\n    {property_name}: {property_type}"

    # Add accessors from model
    pyi_content = pyi_content + "\n\n    # Add accessors from model."
    for accessor_name, accessor_type in accessors.items():
        pyi_content += f"\n    {accessor_name}: {accessor_type}"

    # Add relationships from model
    pyi_content = pyi_content + "\n\n    # Add relationships from model."
    for relationship in relationships:
        pyi_content += f"\n    {relationship['name']}: {relationship['type']}"
        try:
            import_item = relationship.get('import').lstrip("'").rstrip("'")
            imports.append(
                f"from {model_data.get('file_relative_path_dotted').replace('.py', '').rstrip('.')}.{import_item} import {import_item}")
        except AttributeError:
            pass

    # Add dynamic wheres from model fields
    pyi_content = pyi_content + "\n\n    # Add dynamic wheres from model fields."
    for method_name, return_type in dynamic_wheres.items():
        pyi_content += f"\n    def {method_name}(value: typing.Any) -> {return_type}: ..."

    # Add methods
    pyi_content = pyi_content + "\n\n    # Add methods from Model & QueryBuilder class files"
    for method_name, return_type in methods.items():
        if not isinstance(return_type, (dict,)) and not method_name.startswith("where_"):
            pyi_content += f"\n    def {method_name}(*args, **kwargs) -> {return_type}: ..."
        else:
            pyi_content += f"\n    def {method_name}({return_type.get('params').rstrip(', ')}) -> {return_type.get('type')}: ..."

    with open(f"{models_dir}/{model_name}.pyi", "w") as f:
        for import_item in imports:
            pyi_content = import_item + "\n" + pyi_content
        pyi_content = pyi_content.replace("from application.models.Self import Self\n", "")
        f.write(pyi_content)
