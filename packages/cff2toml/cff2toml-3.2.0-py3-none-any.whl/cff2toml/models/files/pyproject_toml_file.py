import os
from typing import List
from cff2toml.models.agents.authors.pyproject_toml_author import PyprojectTomlAuthor
from cff2toml.models.files.metadata_file import DEFAULT_DIR
from cff2toml.models.files.toml_file import TomlFile

DEFAULT_PYPROJECT_TOML_FILENAME: str = 'pyproject.toml'

DEFAULT_PYPROJECT_TOML_FILE_PATH: str = os.path.join(
    DEFAULT_DIR, DEFAULT_PYPROJECT_TOML_FILENAME)


class PyprojectTomlFile(TomlFile):

    def __init__(self, file_path: str = DEFAULT_PYPROJECT_TOML_FILE_PATH):
        super().__init__(file_path=file_path)

    @property
    def metadata_project_version(self):
        return self.get_metadata("project.version")

    @property
    def metadata_project_name(self):
        return self.get_metadata("project.name")

    @property
    def metadata_project_license(self):
        return self.get_metadata("project.license")

    @property
    def metadata_project_description(self):
        return self.get_metadata("project.description")

    @property
    def metadata_project_authors(self):
        return self.get_metadata("project.authors", default_value=[])

    @property
    def metadata_project_urls_source(self):
        return self.get_metadata("project.urls.Source")

    @property
    def authors(self) -> List[PyprojectTomlAuthor]:
        pyproject_toml_authors: List[PyprojectTomlAuthor] = [PyprojectTomlAuthor.model_validate(
            author_metadata) for author_metadata in self.metadata_project_authors]
        return pyproject_toml_authors
