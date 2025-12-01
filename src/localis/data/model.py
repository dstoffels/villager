from dataclasses import dataclass, asdict, fields
import json
from collections import defaultdict


def extract_base(from_obj, depth=1):
    """Returns an instance of a base class populated with subclass obj data. Depth indicates how many levels up the MRO to go."""
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
    LOOKUP_FIELDS: tuple[str] = ()

    FILTER_FIELDS: dict[str, tuple[str]] = defaultdict(tuple)
    """Fields that can be used for filtering. Key is the filter name, value is a tuple of field names to search on."""

    SEARCH_FIELDS: dict[str, float] = {}
    """Fields that can be used for searching. Key is the field name (can be nested with dots), value is the weight for search relevance."""

    search_tokens: str = ""

    @property
    def dto(self) -> DTO:
        return extract_base(self)

    _search_values: list[tuple[str, float]] | None = None

    @property
    def search_values(self) -> list[tuple[str, float]]:
        if self._search_values is None:
            self._search_values = []
            for field, weight in self.SEARCH_FIELDS.items():
                obj = self
                for nested in field.split("."):
                    value: str | list[str] = getattr(obj, nested)
                    if value is None:
                        break
                    obj = value

                if isinstance(value, list):
                    self._search_values.append(([v.lower() for v in value], weight))

                elif value is not None:
                    self._search_values.append((value.lower(), weight))
        return self._search_values
