import villager
import time
from rapidfuzz import fuzz


start = time.perf_counter()
results = villager.cities.search("new york", limit=10)
end = time.perf_counter()

print(end - start)

for r, score in results:
    print(r.display_name, r.population, score)


# original, mangled = ["Musaffa|Musaffah City|Msfh", "Mskh"]

# score = fuzz.partial_token_sort_ratio(original, mangled)
# print(score)
