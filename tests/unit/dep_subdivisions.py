import pytest
from localis import subdivisions, Subdivision


class TestFilter:
    """FILTER"""

    @pytest.mark.parametrize("field", ["type", "country"])
    def test_fields(self, field: str):
        """should return a list of subdivisions where the field kwarg is in:"""
        sub = subdivisions.get(1)
        value = getattr(sub, field)
        if hasattr(value, "alpha2"):
            value = value.alpha2
        results = subdivisions.filter(**{field: value})

        assert len(results) > 0, "should return at least 1"
        assert sub in results, f"subject ({sub.name}) should be in results: {results}"

    def test_aliases(self):
        """should return a list of subdivisions where its aliases field contains the alias value"""

        sub = subdivisions.get(1)
        print(sub.name)

        alias = sub.aliases[0]  # grab the first alias
        results = subdivisions.filter(name=alias)

        assert len(results) > 0, "should return at least 1"
        assert sub in results
