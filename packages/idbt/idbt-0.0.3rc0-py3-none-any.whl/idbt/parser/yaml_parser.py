from idbt.manifest.base import BaseDefinition
from idbt.manifest.i_unit_test import IUnitTestDefinition
from .base import BaseParser
from typing import List
from pydantic import ValidationError
import yaml
from dbt.exceptions import (
    CompilationError,
)

"""
YamlParser read file content and return IUnitTestDefinition
"""


class YamlParser(BaseParser):
    def __init__(self) -> None:
        super().__init__()

    def parse(self, file_path: str) -> List[BaseDefinition]:
        parsed_definitions = []

        try:
            with open(file_path, "r") as file:
                # Load YAML content
                yaml_content: dict = yaml.safe_load(file)

                # parse i_unit_tests
                parsed_definitions = parsed_definitions + self._parse_unit_test_contents(
                    yaml_content, file_path
                )

        except FileNotFoundError:
            raise CompilationError(f"File '{file_path}' not found.")
        except yaml.YAMLError as e:
            raise CompilationError(f"Error parsing YAML file '{file_path}': {e}")
        except ValidationError as e:
            raise CompilationError(str(e))
        return parsed_definitions

    def _parse_unit_test_contents(
        self, yaml_content: str, file_path: str
    ) -> List[IUnitTestDefinition]:
        result: List[IUnitTestDefinition] = []
        if "i_unit_tests" in yaml_content:
            for test_case in yaml_content["i_unit_tests"]:
                test_case["file_path"] = file_path
                definition = IUnitTestDefinition.model_validate(test_case)
                result.append(definition)
        return result
