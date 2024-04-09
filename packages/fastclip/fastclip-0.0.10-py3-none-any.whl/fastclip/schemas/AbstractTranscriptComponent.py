from abc import abstractmethod
import json

from pydantic import BaseModel


class AbstractTranscriptComponent(BaseModel):
    @abstractmethod
    def to_json(self) -> dict:
        """Converts the object to a dictionary."""

    @classmethod
    def from_dict(cls, d):
        """Converts a dictionary to an object."""

    def to_json_str(self) -> str:
        """Converts the object to a JSON string."""

        obj = self.to_json()
        return json.dumps(obj, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str):
        """Converts a JSON string to an object."""

        d = json.loads(json_str)
        return cls.from_dict(d)
