import traceback

def out(*args):
    print("I'm out.")
    for a in args:
        print(a)
    traceback.print_stack()
    exit(77)
