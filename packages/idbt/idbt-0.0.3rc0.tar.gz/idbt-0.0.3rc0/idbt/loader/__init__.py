from idbt.manifest import IdbtManifest
from typing import Dict, Type, List

from idbt.parser.base import BaseParser
from idbt.parser.yaml_parser import YamlParser
import os

"""
FileLoader is used to loop all dbt project folder and load indicated manifest or filepath
"""


class FileLoader:
    parser_classes: Dict[str, Type[BaseParser]] = {"yaml": YamlParser, "yml": YamlParser}
    registered_parsers: Dict[str, BaseParser] = {}

    def __init__(self, file_extensions: List[str] = ["yaml", "yml"]) -> None:
        for file_extension in file_extensions:
            if self.parser_classes.__contains__(file_extension):
                self.registered_parsers[file_extension] = self.parser_classes[file_extension]()

    def load(self, folder_paths: List[str]) -> IdbtManifest:
        """
        Loop folder, get file extension and used registered parser to get definitions
        """
        manifest = IdbtManifest()
        for folder_path in folder_paths:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_extension = os.path.splitext(file)[1][1:]
                    if file_extension in self.registered_parsers:
                        parser = self.registered_parsers[file_extension]
                        file_path = os.path.join(root, file)
                        definitions = parser.parse(file_path)
                        manifest.update(definitions)
        return manifest
