from villager.db.models import CountryModel, CityModel, SubdivisionModel
import time

query = "san fran"

start = time.perf_counter()
for i in range(100):
    results = CityModel.fts_match("san francisco ca", limit=100, exact_match=True)
end = time.perf_counter()

print()
for r in results:
    print(r)


print(f"Took {round((end - start) * 1000,2)}ms")
