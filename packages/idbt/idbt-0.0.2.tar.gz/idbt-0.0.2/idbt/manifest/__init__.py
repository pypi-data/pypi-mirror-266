from dataclasses import dataclass, field

from idbt.manifest.base import BaseDefinition
from .i_unit_test import IUnitTestDefinition
from typing import Dict, List

"""
Manifest contains all customized loaded definition
"""


@dataclass
class IdbtManifest:
    i_unit_test: Dict[str, List[IUnitTestDefinition]] = field(default_factory=lambda: {})

    def update(self, definitions: List[BaseDefinition]):
        for definition in definitions:
            if isinstance(definition, IUnitTestDefinition):
                self._update_i_unit_test_definition(definition)

    def _update_i_unit_test_definition(self, definition: IUnitTestDefinition):
        model = definition.model
        if model in self.i_unit_test:
            self.i_unit_test[model].append(definition)
        else:
            self.i_unit_test[model] = [definition]
