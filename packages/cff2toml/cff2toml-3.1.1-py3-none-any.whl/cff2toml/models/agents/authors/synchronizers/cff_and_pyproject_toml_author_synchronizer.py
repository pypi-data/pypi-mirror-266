from typing import Any, Dict, Union

from cff2toml.models.agents.authors.cff_entity_author import CffEntityAuthor
from cff2toml.models.agents.authors.cff_person_author import CffPersonAuthor
from cff2toml.models.agents.authors.pyproject_toml_author import PyprojectTomlAuthor
from cff2toml.models.agents.people.human_name import HumanName
from cff2toml.models.files.cff_file import CffAuthor

CffAuthorData = Dict[str, Any]
PyprojectTomlAuthorData = Dict[str, Any]

Author = Union[CffPersonAuthor, CffEntityAuthor, PyprojectTomlAuthor]


class CffAndPyprojectTomlAuthorSynchronizer():

    # https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md#how-to-deal-with-unknown-individual-authors
    @staticmethod
    def to_valid_cff_author(author: Author) -> CffAuthor:
        if isinstance(author, CffPersonAuthor) or isinstance(author, CffEntityAuthor):
            author = author.model_copy(deep=True)
            if isinstance(author, CffPersonAuthor) and not author.given_names and not author.family_names:
                # the cff person author has been changed to an anonymous entity author
                entity_author: CffEntityAuthor = CffEntityAuthor()
                entity_author.name = "anonymous"
                entity_author.email = author.email
                entity_author.orcid = author.orcid
                entity_author.address = author.address
                entity_author.city = author.city
                entity_author.alias = author.alias
                entity_author.country = author.country
                entity_author.fax = author.fax
                entity_author.post_code = author.post_code
                entity_author.region = author.region
                entity_author.tel = author.tel
                entity_author.website = author.website
                author = entity_author
            return author
        elif isinstance(author, PyprojectTomlAuthor):
            name: HumanName = HumanName()
            name.full_name = author.name

            cff_author: CffAuthor
            if not name.first_name and not name.last_name:
                cff_author = CffEntityAuthor()
                cff_author.name = "anonymous"
                if author.email:
                    cff_author.email = author.email
            else:
                cff_author = CffPersonAuthor()
                if name.first_name:
                    if name.middle_name:
                        cff_author.given_names = name.first_name + ' ' + name.middle_name
                    else:
                        cff_author.given_names = name.first_name
                if name.particle:
                    cff_author.name_particle = name.particle
                if name.last_name:
                    cff_author.family_names = name.last_name
                if name.suffix:
                    cff_author.name_suffix = name.suffix
                if author.email:
                    cff_author.email = author.email

            return cff_author
        else:
            raise TypeError(
                "Cannot convert to CFF author. Should be an instance of CffAuthor or PyprojcetTomlAuthor.")

    @staticmethod
    def to_cff_author_data(author: Author) -> CffAuthorData:
        author = CffAndPyprojectTomlAuthorSynchronizer.to_valid_cff_author(
            author)
        if isinstance(author, CffPersonAuthor) or isinstance(author, CffEntityAuthor):
            return author.model_dump(mode="json", exclude_defaults=True, by_alias=True)
        else:
            raise TypeError(
                "Cannot convert to CFF author data. Should be an instance of CffAuthor or PyprojcetTomlAuthor.")

    @staticmethod
    def to_valid_pyproject_toml_author(author: Author) -> PyprojectTomlAuthor:
        if isinstance(author, PyprojectTomlAuthor):
            return author
        elif isinstance(author, CffPersonAuthor) or isinstance(author, CffEntityAuthor):
            pyproject_toml_author: PyprojectTomlAuthor = PyprojectTomlAuthor()
            if isinstance(author, CffPersonAuthor):
                pyproject_toml_author.name = ' '.join(
                    [author.given_names, author.name_particle, author.family_names, author.name_suffix])
                pyproject_toml_author.email = author.email
            elif isinstance(author, CffEntityAuthor):
                pyproject_toml_author.name = author.name
            else:
                raise TypeError(
                    "Cannot convert to PyprojectToml author. Should be an instance of CffAuthor or PyprojcetTomlAuthor.")
            return pyproject_toml_author
        else:
            raise TypeError(
                "Cannot convert to PyprojectToml author. Should be an instance of CffAuthor or PyprojcetTomlAuthor.")

    @staticmethod
    def to_pyproject_toml_author_data(author: Author) -> PyprojectTomlAuthorData:
        if isinstance(author, CffPersonAuthor) or isinstance(author, CffEntityAuthor):
            author = CffAndPyprojectTomlAuthorSynchronizer.to_valid_pyproject_toml_author(
                author)
        if isinstance(author, PyprojectTomlAuthor):
            return author.model_dump(mode="json", exclude_defaults=True, by_alias=True)
        else:
            raise TypeError(
                "Cannot convert to Pyproject TOML data. Should be an instance of CffAuthor or PyprojcetTomlAuthor.")
