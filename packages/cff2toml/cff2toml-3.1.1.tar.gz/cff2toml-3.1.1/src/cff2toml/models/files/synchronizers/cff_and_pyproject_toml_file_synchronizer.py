from typing import Any, Dict, List, Tuple, Union
from cff2toml.models.agents.authors.pyproject_toml_author import PyprojectTomlAuthor
from cff2toml.models.agents.authors.synchronizers.cff_and_pyproject_toml_author_synchronizer import Author, CffAndPyprojectTomlAuthorSynchronizer, CffAuthorData, PyprojectTomlAuthorData
from cff2toml.models.files.cff_file import CffAuthor, CffFile
from cff2toml.models.files.pyproject_toml_file import PyprojectTomlFile

# {common property name} -> (pyproject.toml property path}, {cff property path})
PROPERTY_MAPPINGS: Dict[str, Tuple[str, str]] = {
    "title": ("project.name", "title"),
    "version": ("project.version", "version"),
    "description": ("project.description", "abstract"),
    "license": ("project.license", "license"),
    "code_repository_url": ("project.urls.Source", "repository-code"),
    "authors": ("project.authors", "authors")
}


class CffAndPyprojectTomlFileSynchronizerException(Exception):
    pass


# synchronizer
class CffAndPyprojectTomlFileSynchronizer:

    def __init__(self, cff_file: Union[CffFile, None] = None, pyproject_toml_file: Union[PyprojectTomlFile, None] = None):
        if cff_file is None:
            cff_file = CffFile()
        if pyproject_toml_file is None:
            pyproject_toml_file = PyprojectTomlFile()

        self.cff_file = cff_file
        self.pyproject_toml_file = pyproject_toml_file

    def update_cff_with_pyproject_toml(self, delete_missing_metadata: bool = True) -> None:
        for common_property_name, (pyproject_toml_property_path, cff_property_path) in PROPERTY_MAPPINGS.items():
            value = self.pyproject_toml_file.get_metadata(
                property_path=pyproject_toml_property_path)
            if value is not None:
                if common_property_name == "authors":
                    self._update_cff_with_pyproject_toml_authors(
                        delete_missing_metadata=delete_missing_metadata)
                else:
                    self.cff_file.set_metadata(
                        property_path=cff_property_path, value=value)
            else:
                if delete_missing_metadata:
                    # delete corresponding property in cff
                    # if property is missing in pyproject_toml
                    self.cff_file.delete_metadata(
                        property_path=cff_property_path)

    def _update_cff_with_pyproject_toml_authors(self, delete_missing_metadata: bool = True):
        pyproject_toml_authors: List[PyprojectTomlAuthor] = self.pyproject_toml_file.authors

        # copy the list so it passes the type checker
        authors: List[Author] = list(pyproject_toml_authors)

        # set both files' authors since the the CFF file's author objects may be invalid an they may also need to be updated
        # but only remove the authors section in the
        # cff file if there are no authors in the pyproject toml file
        # and if the delete missing metadata flag is set to true
        if len(authors) or delete_missing_metadata:
            self.set_authors(authors=authors)

    def update_pyproject_toml_with_cff(self, delete_missing_metadata: bool = True) -> None:
        for common_property_name, (pyproject_toml_property_path, cff_property_path) in PROPERTY_MAPPINGS.items():
            value = self.cff_file.get_metadata(property_path=cff_property_path)
            if value is not None:
                if common_property_name == "authors":
                    self._update_pyproject_toml_with_cff_authors(
                        delete_missing_metadata=delete_missing_metadata)
                else:
                    self.pyproject_toml_file.set_metadata(
                        property_path=pyproject_toml_property_path, value=value)
            else:
                if delete_missing_metadata:
                    # delete corresponding property in pyproject_toml
                    # if property is missing in cff
                    self.pyproject_toml_file.delete_metadata(
                        property_path=pyproject_toml_property_path)

    def _update_pyproject_toml_with_cff_authors(self, delete_missing_metadata: bool = True):
        cff_authors: List[CffAuthor] = self.cff_file.authors

        # copy the list so it passes the type checker
        authors: List[Author] = list(cff_authors)

        # set both files' authors since the the pyproject toml file's author objects
        # may be invalid an they may also need to be updated
        # but only remove the authors section in the
        # pyproject toml file if there are no authors in the cff file
        # and if the delete missing metadata flag is set to true
        if len(authors) or delete_missing_metadata:
            self.set_authors(authors=authors)

    def _set_common_property(self, common_property_name: str, value: Any):
        if common_property_name in PROPERTY_MAPPINGS:
            pyproject_toml_property_path: str = PROPERTY_MAPPINGS[common_property_name][0]
            cff_property_path: str = PROPERTY_MAPPINGS[common_property_name][1]
            self.cff_file.set_metadata(cff_property_path, value)
            self.pyproject_toml_file.set_metadata(
                pyproject_toml_property_path, value)
        else:
            raise CffAndPyprojectTomlFileSynchronizerException(
                f"Cannot set common property: {common_property_name} because it cannot be found.")

    def set_version(self, version: str) -> None:
        self._set_common_property(
            common_property_name="version", value=version)

    def set_title(self, title: str) -> None:
        self._set_common_property(common_property_name="title", value=title)

    def set_code_repository_url(self, code_repository_url: str) -> None:
        self._set_common_property(
            common_property_name="code_repository_url", value=code_repository_url)

    def set_description(self, description: str) -> None:
        self._set_common_property(
            common_property_name="description", value=description)

    def set_license(self, license: str) -> None:
        self._set_common_property(
            common_property_name="license", value=license)

    def set_authors(self, authors: List[Author]):
        if len(authors):
            author_data_for_cff: list[CffAuthorData] = [
                CffAndPyprojectTomlAuthorSynchronizer.to_cff_author_data(author=author) for author in authors]
            author_data_for_pyproject_toml: list[PyprojectTomlAuthorData] = [
                CffAndPyprojectTomlAuthorSynchronizer.to_pyproject_toml_author_data(author=author) for author in authors]

            self.cff_file.set_metadata("authors", author_data_for_cff)
            self.pyproject_toml_file.set_metadata(
                "project.authors", author_data_for_pyproject_toml)
        else:
            self.cff_file.delete_metadata("authors")
            self.pyproject_toml_file.delete_metadata("project.authors")

    def save(self):
        self.cff_file.save()
        self.pyproject_toml_file.save()
