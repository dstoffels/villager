from .registry import Registry
from ..db import LocalityModel


class LocalityRegistry(Registry[LocalityModel]):
    """Registry for localities."""

    def __init__(self, db, model):
        super().__init__(db, model)

    def search(self, query, limit=5):
        pass
