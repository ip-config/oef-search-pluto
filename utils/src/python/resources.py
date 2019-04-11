import os, sys, io
from pkgutil import get_loader

# https://stackoverflow.com/questions/5003755/how-to-use-pkgutils-get-data-with-csv-reader-in-python

def _find__main__(path):
    while True:
        head, tail = os.path.split(path)
        if head == "":
            return False
        if tail == "__main__":
            return path
        path = head

configured_package_name = '__main__'
configured_package = None
detected_mode = None

m = sys.modules.get("__main__", None)
print("::::::::::::::::",m)
if m and hasattr(m, "__file__"):
    configured_filebase = getattr(m, "__file__")
    if "__main__" in configured_filebase.split('/'):
        configured_filebase = _find__main__(configured_filebase)
        detected_mode = 'bazel'
        
def initialise(base:str=None, package=None, package_name:str=None):

    global configured_package_name
    global configured_package
    global configured_filebase
    global detected_mode

    if base:
        configured_filebase = _find__main__(base)
        detected_mode = 'filesystem'

    if package:
        configured_package = package

    if package_name:
        configured_package_name = package_name


def textfile(resourceName, as_string=False, as_file=False):
    return resource(resourceName, as_string=as_string, as_file=as_file, open_mode="r")


def textlines(resourceName, as_string=False, as_file=False):
    return resource(resourceName, as_string=as_string, as_file=as_file).decode("utf-8").rstrip("\n").split("\n")

def binaryfile(resourceName, as_string=False, as_file=False):
    return resource(resourceName, as_string=as_string, as_file=as_file)

def resource_list(package):
    loader = get_loader(package)
    print(loader.dir)



def get_module():
    return configured_package or sys.modules.get(configured_package_name) or loader.load_module(configured_package_name)

def resource(resourceName, as_string=False, as_file=True, open_mode="rb"):
    global detected_mode

    if detected_mode == None or detected_mode in [ 'filesystem', 'bazel' ]:
        for filename in [
            os.path.join(configured_filebase, resourceName),
            resourceName,
            os.path.join(configured_filebase, "external", resourceName),
            os.path.join("external", resourceName),
        ]:
            print("Exists?", filename)
            if os.path.exists(filename):
                print("Yes")
                detected_mode = 'filesystem'
                if as_file:
                    print("returning file")
                    return open(filename, open_mode)
                if as_string:
                    print("returning name")
                    return filename
                with open(filename, open_mode) as binary_file:
                    return binary_file.read()
        if detected_mode in [ 'filesystem', 'bazel' ]:
            raise Exception("no")

    detected_mode = 'loader'
    #print("R",package, resourceName)
    mod = get_module()
    loader = get_loader(configured_package_name)
    package_filepath = configured_filebase or mod.__file__
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
            raise ValueError("Can't load resource {}::{}".format(package, resourceName))
    else:
        raise ValueError("Not a loader for resource {}::{}".format(package, resourceName))
    return None
