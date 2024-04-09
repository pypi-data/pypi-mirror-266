from typing import Any

from pydantic import BaseModel
from cff2toml.models.files.cff_file import CffFile
from cff2toml.models.files.pyproject_toml_file import PyprojectTomlFile
from cff2toml.models.files.synchronizers.cff_and_pyproject_toml_file_synchronizer import PROPERTY_MAPPINGS


class CommandMetadataOutput(BaseModel):
    command: str
    cff_file_path: str
    pyproject_toml_file_path: str
    common_metadata_name: str
    cff_file_metadata_name: str = ''
    cff_file_metadata_value_before_command: Any = ''
    cff_file_metadata_value_after_command: Any = ''
    pyproject_toml_file_metadata_name: str = ''
    pyproject_toml_file_metadata_value_before_command: Any = ''
    pyproject_toml_file_metadata_value_after_command: Any = ''

    def setup(self):
        cff_file = CffFile(file_path=self.cff_file_path)
        pyproject_toml_file = PyprojectTomlFile(
            file_path=self.pyproject_toml_file_path)
        self.pyproject_toml_file_metadata_name = PROPERTY_MAPPINGS[self.common_metadata_name][0]
        self.cff_file_metadata_name = PROPERTY_MAPPINGS[self.common_metadata_name][1]
        self.cff_file_metadata_value_before_command = cff_file.get_metadata(
            self.cff_file_metadata_name, '')
        self.pyproject_toml_file_metadata_value_before_command = pyproject_toml_file.get_metadata(
            self.pyproject_toml_file_metadata_name)
        self.cff_file_metadata_value_after_command = self.cff_file_metadata_value_before_command
        self.pyproject_toml_file_metadata_value_after_command = self.pyproject_toml_file_metadata_value_before_command

    def set_after_value(self, value: Any) -> None:
        self.cff_file_metadata_value_after_command = value
        self.pyproject_toml_file_metadata_value_after_command = value
