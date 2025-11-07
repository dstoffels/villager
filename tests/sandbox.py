import villager
import pycountry


results = villager.cities.search("madison wi")


for r in results:
    print(r)
    print()
