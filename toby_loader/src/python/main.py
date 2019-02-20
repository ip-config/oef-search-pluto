import csv
import sys

def load_populations(pop_csv):
    pops = {}
    with open(pop_csv, "r") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
        for row in rows[1:]:
            city = row[1]
            popfrag = row[4]

            pops[city] = pops.get(city,0) + int(popfrag)

    del pops['Not a major town or city']

    return pops

def load_coords(coords_csv):
    coords = {}
    with open(coords_csv, "r") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
        for row in rows[1:]:
            city = row[0]
            coords[city] = (row[3],row[4])
    return coords

def main():
    populations = load_populations(sys.argv[1])
    coords = load_coords(sys.argv[2])

    by_pop = sorted(populations.items(), reverse=True, key=lambda x: x[1])

    for k,pop in by_pop:
        if k in coords:
            print("{},{},{}".format(k, coords[k][0], coords[k][1]))

if __name__ == '__main__':
    main()
