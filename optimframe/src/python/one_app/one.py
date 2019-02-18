from optimframe.src.python.openpopgrid import EnglandPopDistro

import popgrab
import random

def main():
    print("Hello")

    eng = EnglandPopDistro.EnglandPopDistro()
    print("LOADING...")
    eng.load("optimframe/src/data")

    class SetPopVisitor(object):
        def __init__(self):
            pass

        def visit(self,x,y,p):
            popgrab.set_pop(x,y,p)

    eng.visit(SetPopVisitor())

    POPS = [
        (1,        ' '),
        (10,       u"\u2591"),
        (100,      u"\u2592"),
        (1000,     u"\u2593"),
        (10000000, u"\u2588"),
    ]
    for y in range(0, 700):
        row = ""
        for x in range(0, 700):
            p = popgrab.read_pop(x,y)
            c = ' '
            for thresh,s in POPS:
                if p>thresh:
                    c = s
            row += c
        print(row)

    for s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
        popgrab.put(ord(s), random.randint(0, 699), random.randint(0, 699))

    popgrab.run()

    for y in range(0, 700):
        row = ""
        for x in range(0, 700):
            c = popgrab.read_reg(x,y)
            row += chr(c)
        print(row)

    t = 0
    for s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
        c = popgrab.get(ord(s))
        print("{} => {}".format(s, c))
        t += c
    print(t)

if __name__ == "__main__":
    main()
