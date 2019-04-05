#/usr/bin/env python3

import os
import sys
import subprocess

from utils.src.python import SubProc

class DockerSubProc(SubProc.SubProc):
    def __init__(
            self,
            image,
            foreground = False,
            background = False,
            cmd = '/bin/sh',
            verbose = False,
            ports = {},
            sudo = False,
            *args, **kwargs):

        super().__init__(self, *args, **kwargs)

        self.image = image
        self.foreground = foreground
        self.background = background
        self.cmd = cmd
        self.verbose = verbose
        self.ports = {}
        self.sudo = sudo

    def addPort(self, pfrom, pto=None):
        self.ports[pfrom] = pto if pto else pfrom

    def makeDockerArgs(self):
        c = []
        if self.sudo:
            c += [ 'sudo' ]
        c +=  [
            'run'
        ]

        if self.foreground:
            c += [ '-it' ]
        elif self.background:
            c += [ '-d' ]
        else:
            c += [ '-t' ]

        for s,d in self.ports:
            c.extend([
                '-p',
                "{}:{}".format(str(int(s)), str(int(d))),
            ])

        c += [ self.image ]
        c += [ self.cmd ]
        return c

    def run(self, args):
        self.args = []
        self.args.extend(self.makeDockerArgs())
        self.args.extend(self.processArgs(args))

        if self.verbose:
            print('execute:{}'.format(' '.join(self.args)))
        r = super().run("docker", self.args)
        if not r:
            raise Exception("can't launch " + self.image)
