import villager

results = villager.cities.search("madison wisconsin dane county")

print([(r.search_tokens, s) for r, s in results][0])
