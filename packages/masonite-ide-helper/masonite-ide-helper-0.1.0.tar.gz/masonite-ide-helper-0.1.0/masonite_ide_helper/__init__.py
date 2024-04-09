import glob
import os
from pathlib import Path
from typing import Any

from masonite_ide_helper.generator import generate_pyi_content
from masonite_ide_helper.utils import extract_accessor_method, get_properties_with_annotations, \
    get_methods_with_return_types, get_passthrough_methods, to_class, get_project_root


class IdeHelper:
    """
    A utility class for generating Python type hinting stub files (.pyi) for Masonite ORM models.
    """

    def __init__(self, models_dir: str | None = None):
        """
        Initializes an instance of IdeHelper.

        Args:
            models_dir (str | None): The directory path containing the model files. If not provided,
                defaults to "application/models" directory.
        """
        if not models_dir:
            self.models_dir = Path(os.path.join(os.getcwd(), "application/models").replace("\masonite_ide_helper", ""))
        else:
            self.models_dir = Path(models_dir)
        self.models: list[dict[str, Any]] = []

    def get_models(self):
        """
        Retrieves the list of model files from the specified directory and extracts relevant information
        such as class name, module path, properties, and methods with their return types.
        """
        cwd = get_project_root(marker="requirements.txt")
        modules = glob.glob(f"{self.models_dir}/*.py", recursive=True)
        for file_path in modules:
            file_path = Path(file_path)
            module_name = file_path.name.replace(".py", "")
            file_relative_path = file_path.relative_to(cwd)
            file_relative_path_dotted = file_relative_path.as_posix().replace("/", ".").replace(module_name, "").rstrip(
                ".")
            dotted_class_path = f"{file_relative_path_dotted}.{module_name}.{module_name}".replace(".py", "")
            if module_name not in ["__init__", "__pycache__"]:
                try:
                    self.models.append({
                        "name": module_name,
                        "module_path": file_path,
                        "class_name": to_class(f"{dotted_class_path}"),
                        "dotted_class_path": dotted_class_path,
                        "file_relative_path_dotted": file_relative_path_dotted,
                        "properties": [
                            get_properties_with_annotations(to_class(f"{dotted_class_path}"))
                        ],
                        "methods": [
                            get_methods_with_return_types(
                                to_class(f"{dotted_class_path}")) | get_passthrough_methods(
                                to_class(f"{dotted_class_path}"))
                        ],
                        "fields": []
                    })
                except:
                    print(module_name, "encountered an error generating stubs.")
        return self

    def make_pyi_files(self):
        """
        Generates Python type hinting stub files (.pyi) for the models located in the specified directory.
        """
        self.get_models()
        for model in self.models:
            generate_pyi_content(model, models_dir=self.models_dir)


if __name__ == "__main__":
    full_directory_path = os.path.join(os.getcwd(), "application/models")
    ide_helper = IdeHelper()
    ide_helper.make_pyi_files()
