from dataclasses import dataclass, asdict, fields
import json
from collections import defaultdict


def extract_base(from_obj, depth=1):
    """Returns an instance of a base class populated with subclass obj data. Can select from multiple base classes by index."""
    target_cls = from_obj.__class__.__mro__[depth]
    field_names = {f.name for f in fields(target_cls)}
    data = {slot: getattr(from_obj, slot) for slot in field_names}
    return target_cls(**data)


@dataclass(slots=True)
class DTO:
    id: int
    name: str

    def to_dict(self):
        return asdict(self)

    def json(self):
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self):
        return self.json()


class Model(DTO):
    SEARCH_FIELDS: tuple[str] = ()

    search_tokens: str = ""

    @property
    def dto(self) -> DTO:
        return extract_base(self)

    _search_values: list[str] | None = None

    @property
    def search_values(self) -> list[str]:
        if self._search_values is None:
            self._search_values = []
            for field in self.SEARCH_FIELDS:
                obj = self
                for nested in field.split("."):
                    value: str | list[str] = getattr(obj, nested)
                    if value is None:
                        break
                    obj = value

                if isinstance(value, list):
                    for v in value:
                        self._search_values.append(v.lower())
                elif value is not None:
                    self._search_values.append(value.lower())
        return self._search_values

    _search_context: str | None = None

    @property
    def search_context(self):
        if self._search_context is None:
            self._search_context = " ".join(self.search_values)
        return self._search_context

    def set_search_meta(self):
        pass
