import pytest
from localis import subdivisions, Subdivision, countries


class TestGet:
    """GET"""

    @pytest.mark.parametrize("field", ["id", "geonames_code", "iso_code"])
    def test_get(self, field: str, sub: Subdivision, select_random):
        """should fetch a subdivision by field:"""

        # need to pick one with all fields
        i = 1
        while not getattr(sub, field):
            sub = select_random(reg=subdivisions, seed_offset=i)
            i += 1
        # while not sub.geonames_code or not sub.iso_code:
        #     sub = select_random(subdivisions)

        value = getattr(sub, field)
        kwarg = {field: value}
        result = subdivisions.get(**kwarg)

        assert isinstance(result, Subdivision)
        assert getattr(result, field) == value


class TestFilter:
    """FILTER"""

    @pytest.mark.parametrize("field", ["type", "country"])
    def test_fields(self, field: str):
        """should return a list of subdivisions where the field kwarg is in:"""

        sub = subdivisions.get(id=1)  # Andorra La Vella
        value = getattr(sub, field)
        results = subdivisions.filter(**{field: value})

        assert len(results) > 0, "should return at least 1"
        assert sub in results, "subject should be in results"

    def test_alt_names(self):
        """should return a list of subdivisions where its alt_names field contains the alt_name kwarg"""

        sub = subdivisions.get(id=7)  # Saint Julia de Loria

        alt_name = sub.alt_names[0]  # grab the first alias
        results = subdivisions.filter(alt_name=alt_name)

        assert len(results) > 0, "should return at least 1"
        assert sub in results


class TestForCountry:
    """FOR_COUNTRY"""

    def test_empty(self, sub: Subdivision):
        """should return [] with invalid input"""

        results = subdivisions.for_country(alpha2="abcbbd")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_country_code(self, sub: Subdivision):
        """should return a list of subdivisions all of which contain the input country code"""

        results = subdivisions.for_country(alpha2=sub.country_alpha2)

        assert len(results) > 0
        assert all(sub.country_alpha2 == r.country_alpha2 for r in results)

    def test_admin_level_filter(self, sub: Subdivision):
        """should return a country's subdivisions filtered by admin level with the default being 1"""

        results = subdivisions.for_country(alpha2=sub.country_alpha2)

        assert len(results) > 0
        assert all(r.admin_level == 1 for r in results)

        results = subdivisions.for_country(alpha2=sub.country_alpha2, admin_level=2)

        assert len(results) > 0
        assert all(r.admin_level == 2 for r in results)


class TestTypes:
    """TYPES_FOR_COUNTRY"""

    def test_empty(self, sub: Subdivision):
        """should reutrn [] with invalid input"""

        results = subdivisions.types_for_country(alpha2="abcbbd")

        assert isinstance(results, list)
        assert len(results) == 0

    def test_country_and_admin_level(self, sub: Subdivision):
        """should return a list of distinct types for a given country, filtered by admin_level"""

        country = countries.get(alpha2=sub.country_alpha2)
        admin_levels = [None, 1, 2]

        for field in countries.ID_FIELDS:
            map = {field: getattr(country, field)}

            for lvl in admin_levels:
                results = subdivisions.types_for_country(admin_level=lvl, **map)
                filtered_subs = subdivisions.for_country(admin_level=lvl, **map)

                filtered_subs_type_set = set(
                    [
                        s.type
                        for s in filtered_subs
                        if s.type is not None and s.admin_level == lvl
                    ]
                )

                assert len(results) == len(filtered_subs_type_set)
                assert set(results) == filtered_subs_type_set
