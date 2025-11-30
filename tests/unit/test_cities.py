import pytest
from localis import cities, City, subdivisions, Subdivision, Country


class TestGet:
    """GET"""

    @pytest.mark.parametrize("field", ["id"])
    def test_get(self, field: str, city: City):
        """should fetch city by:"""
        value = getattr(city, field)
        result = cities.get(value)
        assert isinstance(
            result, City
        ), f"expected a City, instead returned {result}. {field}: {value}"
        assert getattr(result, field) == value, f"Result: {result}, {field}: {value}"


class TestFilter:
    """FILTER"""

    def test_country(self, city: City):
        """should return a list of cities where its country contains the country kwarg"""
        results = cities.filter(country=city.country.alpha2, limit=10)

        assert len(results) > 0, "should return at least 1"
        assert all(city.country.name in r.country.name for r in results)
