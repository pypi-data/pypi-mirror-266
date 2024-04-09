from typing import Any, Dict
from pydantic import BaseModel
import pydash


class Metadata(BaseModel):
    _metadata: Dict[str, Any] = {}

    def from_dict(self, d: Dict[str, Any]) -> None:
        self._metadata = d

    def to_dict(self) -> Dict[str, Any]:
        return self._metadata.copy()

    def get(self, property_path: str, default_value: Any = None) -> Any:
        return pydash.objects.get(
            obj=self._metadata, path=property_path, default=default_value)

    def set(self, property_path: str, value: Any) -> None:
        self._metadata = pydash.objects.set_(
            obj=self._metadata, path=property_path, value=value)

    def delete(self, property_path: str) -> None:
        if self._metadata is not None:
            data_as_dict: Dict = dict(self._metadata)
            pydash.objects.unset(obj=data_as_dict, path=property_path)
            self._metadata = data_as_dict

    def has(self, property_path: str) -> bool:
        if self._metadata is None:
            return False
        else:
            return pydash.objects.has(self._metadata, path=property_path)
