import subprocess
import psutil
import re


class SubProc(object):
    VAR_SUBST = r'\$\{[^$\{\}]+\}'

    def __init__(self, *args, **kwargs):
        self.varnamesToValues = {}
        self.process = None

    def configure(self, varnamesToValues: dict):
        self.varnamesToValues.update(varnamesToValues)

    def getConfig(self, v):
        if v[0] == '$':
            v = v[2:-1]
        return  self.varnamesToValues.get(v, '')

    def processArgs(self, args):
        r = []
        for a in args:
            while True:
                m = re.search(SubProc.VAR_SUBST, a)
                if m:
                    b =a
                    a = re.sub(
                        SubProc.VAR_SUBST,
                        lambda x: self.getConfig(x.group(0)),
                        a,
                    )
                else:
                    break
            r.append(a)
        return r

    def run(self, binary, args):
        processed_args = self.processArgs(args)
        self.cmdline = ' '.join(processed_args)
        self.process = subprocess.Popen([ binary ] + args)
        return True

def main():
    foo = SubProc()
    foo.configure({'xx': 'XX', 'yy': 'YY', 'zz': 'xx'})
    print(foo.processArgs('moocows', '${${zz}}'))

if __name__ == "__main__":
    main()

