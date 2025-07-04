from typing import Iterator, Generic, TypeVar
from abc import abstractmethod, ABC
import unicodedata, re
from peewee import SqliteDatabase
from ..db.models import BaseModel, DTOModel
from typing import Type

T = TypeVar("T", bound=DTOModel)


class Registry(Generic[T], ABC):
    """Abstract base registry class defining interface for lookup and search."""

    def __init__(self, db: SqliteDatabase, model: Type[T]):
        self._db = db
        self.__model = model
        self._cache: list[T] = self.__model.to_dtos()
        self._lookups_cached = False

    @property
    def count(self) -> int:
        return len(self._cache)

    def __iter__(self) -> Iterator[T]:
        return iter(self._cache)

    def __getitem__(self, index: int) -> T:
        return self._cache[index]

    def __len__(self) -> int:
        return len(self._cache)

    @staticmethod
    def _normalize(s: str) -> str:

        s = s.lower()
        s = (
            unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
        )  # normalize unicode
        s = re.sub(r"[^\w\s]", "", s)  # strip punctuation
        s = re.sub(r"\s+", " ", s).strip()
        return s

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[tuple[T, float]]:
        pass
