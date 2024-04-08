from cff2toml.models.files.cff_file import CffFile
from tests.temp_copied_file import TempCopiedFile
from unittest.mock import patch


def test_load_cff_file(dummy_cff_file_path):
    with TempCopiedFile(source_file_path=dummy_cff_file_path) as tmp_dummy_cff_file:
        cff_file: CffFile = CffFile(file_path=tmp_dummy_cff_file.file_path)
        assert cff_file.get_metadata('version') == '0.0.2'
        assert cff_file.get_metadata('title') == 'somecooltool'
        assert cff_file.get_metadata(
            'abstract') == 'A module that does something cool.'
        assert cff_file.get_metadata('license') == 'Apache-2.0'
        assert cff_file.get_metadata(
            'repository-code') == 'https://github.com/willynilly/somewherecool'


def test_save_cff_file(dummy_cff_file_path):
    with TempCopiedFile(source_file_path=dummy_cff_file_path) as tmp_dummy_cff_file:
        cff_file: CffFile = CffFile(file_path=tmp_dummy_cff_file.file_path)
        assert cff_file.get_metadata('version') == '0.0.2'
        assert cff_file.get_metadata('title') == 'somecooltool'
        assert cff_file.get_metadata(
            'abstract') == 'A module that does something cool.'
        assert cff_file.get_metadata('license') == 'Apache-2.0'
        assert cff_file.get_metadata(
            'repository-code') == 'https://github.com/willynilly/somewherecool'

        assert cff_file.has_metadata('license') == True
        assert cff_file.has_metadata('dogs.live.in.the.house') == False
        assert cff_file.has_metadata(
            'dogs.average_weight') == False

        cff_file.set_metadata('version', '100.0.2')
        cff_file.set_metadata('repository-code', 'https://somewherebad')
        cff_file.set_metadata('dogs.live.in.the.house', 'yes')
        cff_file.set_metadata(
            'dogs.average_weight', 10.1)

        cff_file.save()

        after_save_cff_file: CffFile = CffFile(
            file_path=tmp_dummy_cff_file.file_path)
        assert after_save_cff_file.has_metadata('project.license') == False
        assert after_save_cff_file.get_metadata(
            'version') == '100.0.2'
        assert after_save_cff_file.get_metadata(
            'title') == 'somecooltool'
        assert after_save_cff_file.get_metadata(
            'abstract') == 'A module that does something cool.'
        assert after_save_cff_file.get_metadata(
            'repository-code') == 'https://somewherebad'
        assert after_save_cff_file.get_metadata(
            'dogs.live.in.the.house') == 'yes'
        assert after_save_cff_file.get_metadata(
            'dogs.average_weight') == 10.1


def test_get_version_metadata_for_cff(dummy_cff_file):
    assert dummy_cff_file.metadata_version == '0.0.2'


def test_get_repository_code_metadata_for_cff(dummy_cff_file):
    assert dummy_cff_file.metadata_repository_code == 'https://github.com/willynilly/somewherecool'


def test_get_license_metadata_for_cff(dummy_cff_file):
    assert dummy_cff_file.metadata_license == 'Apache-2.0'


def test_get_title_metadata_for_cff(dummy_cff_file):
    assert dummy_cff_file.metadata_title == 'somecooltool'


def test_get_abstract_metadata_for_cff(dummy_cff_file):
    assert dummy_cff_file.metadata_abstract == 'A module that does something cool.'


def test_get_version_for_cff_with_default_file_path(dummy_cff_file_path):
    with TempCopiedFile(source_file_path=dummy_cff_file_path) as tmp_dummy_cff_file:
        # patch the default parameters in constructor
        # the __defaults__ variable contains
        # the tuple of paramter defaults that can be mocked
        with patch('cff2toml.models.files.cff_file.CffFile.__init__.__defaults__', (tmp_dummy_cff_file.file_path,)):
            cff_file: CffFile = CffFile()
            assert cff_file.metadata_version == '0.0.2'


def test_get_title_for_cff_with_default_file_path(dummy_cff_file_path):
    with TempCopiedFile(source_file_path=dummy_cff_file_path) as tmp_dummy_cff_file:
        # patch the default parameters in constructor
        # the __defaults__ variable contains
        # the tuple of paramter defaults that can be mocked
        with patch('cff2toml.models.files.cff_file.CffFile.__init__.__defaults__', (tmp_dummy_cff_file.file_path,)):
            cff_file: CffFile = CffFile()
            assert cff_file.metadata_title == 'somecooltool'
