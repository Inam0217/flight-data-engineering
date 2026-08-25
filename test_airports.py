from airport_repository import get_airports


airports = get_airports()

print("Number of airports:", len(airports))

for airport in airports:
    print(airport)