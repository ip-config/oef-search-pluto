#!/usr/bin/env python3

import csv
import sys

from optimframe.src.python.openpopgrid import EnglandPopDistro

W = 700
H = 1300
FH = 1000
dots = {}

def main():
    with open(sys.argv[1], "r") as fh:
        r = csv.reader(fh)

        for y in range(0,H):
            dots[y] = {}
            for x in range(0,W):
                dots[y][x] = 0.0

        for i, row in enumerate(r):
            if i == 0:
                continue
            c,x,y = row
            dots[int(y)][int(x)] = float(c)

        for y in range(FH-1,0,-3):
            print(''.join(
                [
                    '#' if dots[y][x]>0.0 else '_'
                    for x
                    in range(0,W,3)
                ]
            ))
        #return
        pop = EnglandPopDistro.EnglandPopDistro()
        pop.load("optimframe/src/data")

        do = pop.unloaded + [ "NT", "NU", "NW", "NX", "NY", "NZ" ]
        for tile in do:
            print("ADDING ", tile)
            whr = pop.getTileRange(tile)
            ((xl, xh), (yl, yh)) = whr
            print(whr)
            for y in range(yl,yh+1):
                print(''.join([
                    '#' if dots[y][x]>0.0 else '_'
                    for x
                    in range(xl,xh+1)
                ]))
            for y in range(yl,yh+1):
                for x in range(xl,xh+1):
                    pop.put(x,y,  dots[700-y][x])
        pop.savePNG()

if __name__ == "__main__":
    main()
