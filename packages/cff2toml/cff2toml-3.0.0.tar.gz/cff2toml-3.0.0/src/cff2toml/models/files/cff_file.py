from typing import List, Union
import yaml
import os
from cff2toml.models.agents.authors.cff_entity_author import CffEntityAuthor
from cff2toml.models.agents.authors.cff_person_author import CffPersonAuthor
from cff2toml.models.files.metadata_file import MetadataFile, DEFAULT_DIR
from cff2toml.models.metadata import Metadata

DEFAULT_CITATION_CFF_FILENAME: str = 'CITATION.cff'
DEFAULT_CITATION_CFF_FILE_PATH: str = os.path.join(
    DEFAULT_DIR, DEFAULT_CITATION_CFF_FILENAME)

CffAuthor = Union[CffPersonAuthor, CffEntityAuthor]


class LoadCffFileException(Exception):
    pass


class SaveCffFileException(Exception):
    pass


class CffFile(MetadataFile):

    def __init__(self, file_path: str = DEFAULT_CITATION_CFF_FILE_PATH):
        super().__init__(file_path=file_path)
        self.file_path = file_path
        try:
            with open(self.file_path, 'r') as cff_file:
                self._metadata.from_dict(yaml.safe_load(cff_file))
        except:
            raise LoadCffFileException(
                f"Cannot load this CFF file: {self.file_path}")

    def save(self, file_path: Union[str, None] = None) -> None:
        if file_path is None:
            file_path = self.file_path
        if self._metadata is not None:
            try:
                with open(file_path, 'w') as cff_file:
                    yaml.safe_dump(self._metadata.to_dict(), cff_file)
            except:
                raise SaveCffFileException(
                    f"Cannot save this CFF file: {file_path}")
        else:
            raise SaveCffFileException(
                f"Cannot save this CFF file: {file_path} because there is no data.")

    @property
    def metadata_version(self):
        return self.get_metadata("version")

    @property
    def metadata_title(self):
        return self.get_metadata("title")

    @property
    def metadata_license(self):
        return self.get_metadata("license")

    @property
    def metadata_abstract(self):
        return self.get_metadata("abstract")

    @property
    def metadata_authors(self):
        return self.get_metadata("authors")

    @property
    def metadata_repository_code(self):
        return self.get_metadata("repository-code")

    @property
    def authors(self) -> List[CffAuthor]:
        cff_authors: List[CffAuthor] = []
        for author_metadata in self.metadata_authors:

            metadata: Metadata = Metadata()
            metadata.from_dict(author_metadata)

            if metadata.has('given-names') or metadata.has('family-names'):
                cff_author: CffAuthor = CffPersonAuthor.model_validate(
                    author_metadata)
            else:
                if not metadata.has('name') or str(metadata.get('name')).strip() == '':
                    metadata.set('name', 'anonymous')
                cff_author: CffAuthor = CffEntityAuthor.model_validate(
                    author_metadata)
            cff_authors.append(cff_author)
        return cff_authors
