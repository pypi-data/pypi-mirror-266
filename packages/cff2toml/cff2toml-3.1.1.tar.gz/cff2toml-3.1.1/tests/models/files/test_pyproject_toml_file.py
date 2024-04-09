from unittest.mock import patch
from cff2toml.models.files.pyproject_toml_file import PyprojectTomlFile
from tests.temp_copied_file import TempCopiedFile


def test_get_project_version_metadata_for_pyproject_toml(dummy_pyproject_toml_file):
    assert dummy_pyproject_toml_file.metadata_project_version == '0.0.1'


def test_get_project_name_metadata_for_pyproject_toml(dummy_pyproject_toml_file):
    assert dummy_pyproject_toml_file.metadata_project_name == 'someuncooltool'


def test_get_project_license_metadata_for_pyproject_toml(dummy_pyproject_toml_file):
    assert dummy_pyproject_toml_file.metadata_project_license == 'Apache-1.0'


def test_get_project_urls_source_metadata_for_pyproject_toml(dummy_pyproject_toml_file):
    assert dummy_pyproject_toml_file.metadata_project_urls_source == 'https://github.com/willynilly/somewhereuncool'


def test_get_project_description_metadata_for_pyproject_toml(dummy_pyproject_toml_file):
    assert dummy_pyproject_toml_file.metadata_project_description == 'A module that does something uncool.'


def test_get_project_version_metadata_for_pyproject_toml_with_default_file_path(dummy_pyproject_toml_file_path):
    with TempCopiedFile(source_file_path=dummy_pyproject_toml_file_path) as tmp_dummy_pyproject_toml_file:
        # patch the default parameters in the constructor.
        # the __defaults__ variable contains
        # the tuple of paramter defaults that can be mocked
        with patch('cff2toml.models.files.pyproject_toml_file.PyprojectTomlFile.__init__.__defaults__', (tmp_dummy_pyproject_toml_file.file_path,)):
            pyproject_toml_file: PyprojectTomlFile = PyprojectTomlFile()
            version: str = pyproject_toml_file.metadata_project_version
            assert version == '0.0.1'


def test_get_project_name_metadata_for_pyproject_toml_with_default_file_path(dummy_pyproject_toml_file_path):
    with TempCopiedFile(source_file_path=dummy_pyproject_toml_file_path) as tmp_dummy_pyproject_toml_file:
        # patch the default parameters in the constructor.
        # the __defaults__ variable contains
        # the tuple of paramter defaults that can be mocked
        with patch('cff2toml.models.files.pyproject_toml_file.PyprojectTomlFile.__init__.__defaults__', (tmp_dummy_pyproject_toml_file.file_path,)):
            pyproject_toml_file: PyprojectTomlFile = PyprojectTomlFile()
            name: str = pyproject_toml_file.metadata_project_name
            assert name == 'someuncooltool'
