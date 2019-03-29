import os, sys, io
from pkgutil import get_loader

# https://stackoverflow.com/questions/5003755/how-to-use-pkgutils-get-data-with-csv-reader-in-python

main_package = '__main__'
inside_bazel = None

def initialise(package):
    global main_package
    main_package = package
    assert main_package != None

def textfile(resourceName, as_string=False, as_file=False):
    return resource(main_package, resourceName, as_string=as_string, as_file=as_file).decode("utf-8")


def textlines(resourceName, as_string=False, as_file=False):
    return resource(main_package, resourceName, as_string=as_string, as_file=as_file).decode("utf-8").rstrip("\n").split("\n")


def binaryfile(resourceName, as_string=False, as_file=False):
    return resource(main_package, resourceName, as_string=as_string, as_file=as_file)

def resource_list(package):
    loader = get_loader(package)
    print(loader.dir)

def _find__main__(path):
    while True:
        head, tail = os.path.split(path)
        if head == "":
            return False
        if tail == "__main__":
            return path
        path = head

def resource(package, resourceName, as_string=False, as_file=True):
    #print("R",package, resourceName)
    loader = get_loader(package)
    mod = sys.modules.get(package) or loader.load_module(package)
    package_filepath = mod.__file__
    if mod != None and hasattr(mod, '__file__'):
        # Modify the resourceName name to be compatible with the loader.get_data
        # signature - an os.path format "filename" starting with the dirname of
        # the package's __file__
        #parts = resourceName.split('/')
        #resource_name = os.path.join(*parts)
        #parts.insert(0, os.path.dirname(mod.__file__))
        full_resource_name = resourceName#os.path.join(*parts)
    if loader == None:
        raise ValueError("No loader available for resource {}::{}".format(package, resourceName))
    if hasattr(loader, 'get_data'):
        if as_string:
            return resourceName
        else:
            try:
                if as_file:
                    return io.BytesIO(loader.get_data(full_resource_name))
                return loader.get_data(full_resource_name)
            except OSError as ex:
                if ex.errno != 2:
                    raise

            if os.path.exists(resourceName):
                if as_file:
                    return open(resourceName, "rb")
                with open(resourceName, "rb") as binary_file:
                    return binary_file.read()

            global inside_bazel
            if inside_bazel == None:
                inside_bazel = _find__main__(package_filepath)

            if inside_bazel:
                poss_path = os.path.join(inside_bazel, resourceName)
                if os.path.exists(poss_path):
                    if as_file:
                        return open(poss_path, "rb")
                    with open(poss_path, "rb") as binary_file:
                        return binary_file.read()
            raise ValueError("Can't load resource {}::{}".format(package, resourceName))
    else:
        raise ValueError("Not a loader for resource {}::{}".format(package, resourceName))
    return None
