import villager
import time

start = time.perf_counter()
results = villager.cities.search("sam fransisko", limit=10)
end = time.perf_counter()

for r, s in results:
    print(r.display_name, s)

print(f"Search took {(end - start) * 1000} ms")
