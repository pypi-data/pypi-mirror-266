from typing import Any

from pydantic import BaseModel

from cff2toml.models.metadata import Metadata

DEFAULT_DIR: str = '.'


class MetadataFile(BaseModel):

    _metadata: Metadata = Metadata()
    file_path: str = ''

    def get_metadata(self, property_path: str, default_value: Any = None) -> Any:
        return self._metadata.get(property_path=property_path, default_value=default_value)

    def set_metadata(self, property_path: str, value: Any) -> None:
        self._metadata.set(property_path=property_path, value=value)

    def delete_metadata(self, property_path: str) -> None:
        if self._metadata is not None:
            self._metadata.delete(property_path=property_path)

    def has_metadata(self, property_path: str) -> bool:
        return self._metadata.has(property_path=property_path)
