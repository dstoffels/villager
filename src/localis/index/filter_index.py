class FilterIndex:
    """Indexes by field and value"""

    def __init__(self, **kwargs):
        self.index: dict[str, dict[str, set[int]]] = {}

    def add(self, field: str, value: str | int, id: int):
        if field not in self.index:
            self.index[field] = {}
        field_index = self.index[field]
        if value not in field_index:
            field_index[value] = set()
        field_index[value].add(id)

    def get(self, field: str, value: str):
        return self.index.get(field, {}).get(value, set())
