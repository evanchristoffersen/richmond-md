#!/usr/bin/env python 

import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management




__authors__ = 'Evan Christoffersen', 'Konnor Jones'
# __license__
# __version__



class MyFileList(list):

    name = ''

    def listall(self):
        for index, item in enumerate(self):
            print(str(index+1) + ":", self[index])

    def strings(self):
        return [str(item) for item in self]



class MyFileList(list):
    name = ''
    def showall(self):
        for index, item in enumerate(self):
            print(str(index+1) + ":", self[index])

    def convert(self, dtype):
        if dtype == str:
            for i in range(len(self)):
                self[i] = str(self[i])
        elif dtype == int:
            for i in range(len(self)):
                self[i] = int(self[i])
        else:
            return self
        return self

    def cleanup(self):
        # Remove empty items
        self = [item for item in self if "" is not item]
        # Remove duplicate items
        self = list(dict.fromkeys(self))
        # Remove whitespace (including \t and \n)
        self = ["".join(str(item).split()) for item in self]
        return self
    
    def flatten(self):
        if isinstance(self, collections.Iterable):
            return [a for i in self for a in self.flatten(self)]
        else:
            return self
    # def flatten(self):
    #     out = []
    #     for sublist in self:
    #         for item in sublist:
    #             out.append(item)
    #     self = out
    #     # out = [item for sublist in self for item in sublist]
    #     # self = []
    #     # self = out
    #     return self
    
    # def flatten(self):
    #     for item in self:
    #         if isinstance(item, Iterable) and not isinstance(item, (str,bytes)):
    #             yield from flatten(item)
    #         else:
    #             yield item
                
    # def flattengenerator(self):
    #     for i in self:
    #         if isinstance(i, (list,tuple)):
    #             for j in flatten(i):
    #                 yield j
    #         else:
    #             yield i




