from pytest import fixture
from cff2toml.models.files.metadata_file import MetadataFile


@fixture
def dummy_metadata_file():
    metadata_file = MetadataFile()
    metadata_file._metadata.from_dict({'some': {'nestedproperty': 'somedata'}})
    return metadata_file


def test_get_metadata_for_existing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.nestedproperty') == True
    assert dummy_metadata_file.get_metadata(
        'some.nestedproperty') == 'somedata'


def test_get_metadata_for_missing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.missing.property') == False
    assert dummy_metadata_file.get_metadata('some.missing.property') == None


def test_has_metadata_for_existing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.nestedproperty') == True


def test_has_metadata_for_missing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('cat') == False


def test_set_metadata_for_existing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.nestedproperty') == True
    dummy_metadata_file.set_metadata(
        'some.nestedproperty', 'somedifferentdata')
    assert dummy_metadata_file.get_metadata(
        'some.nestedproperty') == 'somedifferentdata'


def test_set_metadata_for_missing_property(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.missing.property') == False
    dummy_metadata_file.set_metadata('some.missing.property', 'moredata')
    assert dummy_metadata_file.get_metadata(
        'some.missing.property') == 'moredata'


def test_delete_metadata_for_existing_data(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.nestedproperty') == True
    dummy_metadata_file.delete_metadata('some.nestedproperty')
    assert dummy_metadata_file.has_metadata('some.nestedproperty') == False


def test_delete_metadata_for_missing_data(dummy_metadata_file):
    assert dummy_metadata_file.has_metadata('some.missing.property') == False
    dummy_metadata_file.delete_metadata('some.missing.property')
    assert dummy_metadata_file.has_metadata('some.missing.property') == False
