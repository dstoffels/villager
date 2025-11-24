from typing import Generic, TypeVar
from localis.data import DTO
from collections import defaultdict

TDTO = TypeVar("TDTO", bound=DTO)


class Index(Generic[TDTO]):
    def __init__(self, **kwargs):
        self._index: dict[int | str, set[TDTO]] = defaultdict(set)

    def add(self, key: int | str, DTO: TDTO, **kwargs):
        if isinstance(key, str):
            key = key.lower()

        self._index[key].add(DTO)

    def get(self, key: int | str, **kwargs) -> set[TDTO]:
        return self._index.get(key.lower())
