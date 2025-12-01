from localis import countries, Country
import pytest


class TestGet:
    """GET"""

    @pytest.mark.parametrize("field", ["id", "alpha2", "alpha3", "numeric"])
    def test_get(self, field: str, country: Country):
        """should fetch a country by:"""
        value = getattr(country, field)
        result = countries.get(value)
        assert isinstance(result, Country)
        assert getattr(result, field) == value


class TestFilter:
    """FILTER"""

    def test_filter_by_official_name(self, country: Country, select_random):
        """should filter results by country's official_name field"""

        while not country.official_name:
            country = select_random(countries, country.id + 1)

        results = countries.filter(name=country.official_name)

        assert len(results) > 0, "should have at least 1 result"
        assert country in results

    def test_filter_by_alt_name(self, country: Country, select_random):
        """should filter results by country's alt_names field"""

        i = 1
        while not country.aliases:
            country = select_random(countries, i)
            i += 1

        alt_name = country.aliases[0]
        results = countries.filter(name=alt_name)

        assert len(results) > 0, "should have at least 1 result"
        assert all(alt_name in r.aliases for r in results)
