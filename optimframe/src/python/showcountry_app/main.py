
from optimframe.src.python.openpopgrid import EnglandPopDistro

def main():
    eng = EnglandPopDistro.EnglandPopDistro()
    print("LOADING...")
    eng.load("optimframe/src/data")
    eng.print()

if __name__ == "__main__":
    main()
