from .base import BaseDefinition
from typing import List, Optional, Any
from pydantic import BaseModel, model_validator
import pathlib
import os


class AssertMacroParameter(BaseModel):
    key: str
    value: Any


class Given(BaseModel):
    input: str
    file: str


class AssertMacro(BaseModel):
    name: str
    parameters: List[AssertMacroParameter]


class IUnitTestDefinition(BaseDefinition):
    model: str
    name: str
    description: Optional[str]
    given: List[Given]
    expected_output_file: Optional[str]
    assert_macro: AssertMacro
    file_path: str

    @model_validator(mode="after")
    def post_check(self) -> "IUnitTestDefinition":
        if self.expected_output_file and os.path.exists(self.expected_output_file) == False:
            raise ValueError(
                f"""expected_output_file: {self.expected_output_file} not found in unitest: {self.file_path}.
                    Please recheck the unittest yaml file {self.file_path}"""
            )

        for given_input in self.given:
            if os.path.exists(given_input.file) == False:
                raise ValueError(
                    f"""given.file: {given_input.file} not found in unitest: {self.file_path}.
                    Please recheck the unittest yaml file {self.file_path}
                    """
                )

        return self
