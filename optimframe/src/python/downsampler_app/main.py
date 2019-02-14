#!/usr/bin/env python3

import os

from optimframe.src.python.openpopgrid import OpenPopGridTile

def main():
    for fn in [
         "NU",

         "NT",
         "NX",
         "NY",
         "NZ",
         "SD",
         "SE",
         "SH",
         "SJ",
         "SK",
         "SM",
         "SN",
         "SO",
         "SP",
         "SR",
         "SS",
         "ST",
         "SU",
         "SV",
         "SW",
         "SX",
         "SY",
         "SZ",
         "TA",
         "TF",
         "TG",

         "TL",
         "TM",
         "TQ",
         "TR",
         "TV",
    ]:
        tile = OpenPopGridTile.OpenPopGridTile()
        with open(os.path.join("optimframe/src/data", fn + ".asc"), "r") as f:
            tile.load(f)
        tile.print()
        with open(os.path.join("optimframe/src/data", fn + ".pop-dist.km.txt"), "w") as f:
            tile.save(f)

if __name__ == "__main__":
    main()
