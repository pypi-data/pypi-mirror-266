from pytest import fixture
from cff2toml.models.agents.authors.synchronizers.cff_and_pyproject_toml_author_synchronizer import CffAndPyprojectTomlAuthorSynchronizer


@fixture
def author_synchronizer():
    return CffAndPyprojectTomlAuthorSynchronizer


def test_to_cff_data_with_all_parts(author_synchronizer, dummy_cff_author_person):

    assert dummy_cff_author_person.given_names == 'Billy Bob'
    assert dummy_cff_author_person.name_particle == 'de'
    assert dummy_cff_author_person.family_names == 'Longshot'
    assert dummy_cff_author_person.name_suffix == 'VIII'
    assert dummy_cff_author_person.email == 'longshot@somewherecool.nl'

    cff_author_data = author_synchronizer.to_cff_author_data(
        dummy_cff_author_person)

    assert cff_author_data['given-names'] == 'Billy Bob'
    assert cff_author_data['name-particle'] == 'de'
    assert cff_author_data['family-names'] == 'Longshot'
    assert cff_author_data['name-suffix'] == 'VIII'
    assert cff_author_data['email'] == 'longshot@somewherecool.nl'


def test_to_cff_data_uses_anonymous_when_missing_first_name_and_last_name(author_synchronizer, dummy_cff_author_person):

    assert dummy_cff_author_person.given_names == 'Billy Bob'
    assert dummy_cff_author_person.name_particle == 'de'
    assert dummy_cff_author_person.family_names == 'Longshot'
    assert dummy_cff_author_person.name_suffix == 'VIII'
    assert dummy_cff_author_person.email == 'longshot@somewherecool.nl'

    dummy_cff_author_person.given_names = ''
    dummy_cff_author_person.family_names = ''

    cff_author_data = author_synchronizer.to_cff_author_data(
        dummy_cff_author_person)

    assert cff_author_data['name'] == 'anonymous'
    assert cff_author_data['email'] == 'longshot@somewherecool.nl'

    # the cff author is assumed to be an entity, and entities lack the following:
    assert 'given-names' not in cff_author_data
    assert 'name-particle' not in cff_author_data
    assert 'family-names' not in cff_author_data
    assert 'name-suffix' not in cff_author_data
    assert 'affiliation' not in cff_author_data  # entities do not have affiliation


def test_to_pyproject_toml_data_with_all_parts(author_synchronizer, dummy_cff_author_person):

    assert dummy_cff_author_person.given_names == 'Billy Bob'
    assert dummy_cff_author_person.name_particle == 'de'
    assert dummy_cff_author_person.family_names == 'Longshot'
    assert dummy_cff_author_person.name_suffix == 'VIII'
    assert dummy_cff_author_person.email == 'longshot@somewherecool.nl'

    pyproject_toml_author_data = author_synchronizer.to_pyproject_toml_author_data(
        dummy_cff_author_person)

    assert pyproject_toml_author_data['name'] == 'Billy Bob de Longshot VIII'
    assert pyproject_toml_author_data['email'] == 'longshot@somewherecool.nl'
