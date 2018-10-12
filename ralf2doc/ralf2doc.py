#!/usr/bin/env python
# -*- coding: utf-8 -*-

' this script generates register docs based on ralf file '

__author__ = "Bo DONG"

import sys, os
import re

from ralf_class import *

def func():
    return "Hello World!"


def main():
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: {} TARGET RALF_FILE <CSV_FILE>".format(os.path.basename(__file__)))
    else:
        target = sys.argv[1]
        ralf = sys.argv[2]
        csv = None
        if len(sys.argv) == 4:
            csv = sys.argv[3]

        if not os.path.isfile(ralf):
            print("{} is not a valid file".format(ralf))
        else:
            hier = [] # hierachy list
            defs = [] # define list
            with open(ralf) as f:
                for nu, l in enumerate(f):
                    l = l.strip()
                    level = len(hier)
                    # end of definition
                    if re.search(r"^}", l):
                        item = hier.pop(-1)
                        # add to defs if top level
                        if level == 1:
                            defs.append(item)
                        # print 
                        if item.name == target:
                            print(item)
                            # generate csv file
                            if csv:
                                with open(csv, 'w') as c:
                                    c.write(item.csv())
                    # info
                    elif re.search(r"^#\s*(.*)", l):
                        match = re.search(r"^#\s*(.*)", l)
                        hier[-1].info += match.group(1)
                    # bits
                    elif re.search(r"^bits\s+(\d+)\s*;", l):
                        match = re.search(r"^bits\s+(\d+)\s*;", l)
                        hier[-1].bits = int(match.group(1))
                    # access
                    elif re.search(r"^access\s+(\w+)\s*;", l):
                        match = re.search(r"^access\s+(\w+)\s*;", l)
                        hier[-1].access = match.group(1)
                    # reset
                    elif re.search(r"^reset\s+(\S+)\s*;", l):
                        match = re.search(r"^reset\s+(\S+)\s*;", l)
                        hier[-1].reset = match.group(1)
                    # bytes
                    elif re.search(r"^bytes\s+(\d+)\s*;", l):
                        match = re.search(r"^bytes\s+(\d+)\s*;", l)
                        hier[-1].bytes = match.group(1)
                    # endian
                    elif re.search(r"^endian\s+(\w+)\s*;", l):
                        match = re.search(r"^endian\s+(\w+)\s*;", l)
                        hier[-1].endian = match.group(1)
                    # size
                    elif re.search(r"^size\s+(\w+)\s*;", l):
                        match = re.search(r"^size\s+(\w+)\s*;", l)
                        hier[-1].size = match.group(1)
                    # leftright
                    elif re.search(r"^left_to_right\s*;", l):
                        match = re.search(r"^left_to_right\s*;", l)
                        hier[-1].leftright = True

                    # field
                    elif re.search(r"^field", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^field\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^field\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^field\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^field\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^field\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^field\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^field\s+(\w+)", l): # name
                            match = re.search(r"^field\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported field format in line {}: '{}'".format(nu, l))

                        field = Field(level=level, name=name, offset=offset, path=path)

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Field" in str(type(d)):
                                    field = d
                                    field.level, field.offset, field.path = level, offset, path
                            hier[-1].fields.append(field)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(field)
                            
                    # register
                    elif re.search(r"^register", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^register\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^register\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^register\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^register\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^register\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^register\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^register\s+(\w+)", l): # name
                            match = re.search(r"^register\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported register format in line {}: '{}'".format(nu, l))

                        register = Register(level=level, name=name, offset=offset, path=path, fields=[])

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Register" in str(type(d)):
                                    register = d
                                    register.level, register.offset, register.path = level, offset, path
                            hier[-1].registers.append(register)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(register) 

                    # regfile
                    elif re.search(r"^regfile", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^regfile\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^regfile\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^regfile\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^regfile\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^regfile\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^regfile\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^regfile\s+(\w+)", l): # name
                            match = re.search(r"^regfile\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported regfile format in line {}: '{}'".format(nu, l))

                        regfile = Regfile(level=level, name=name, offset=offset, path=path, registers=[])

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Regfile" in str(type(d)):
                                    regfile = d
                                    regfile.level, regfile.offset, regfile.path = level, offset, path
                            hier[-1].regfiles.append(regfile)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(regfile) 

                    # virtual register
                    elif re.search(r"^virtual register", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^virtual register\s+(\w+)\s+(\w+)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^virtual register\s+(\w+)\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^virtual register\s+(\w+)", l): # name
                            match = re.search(r"^virtual register\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported virtual register format in line {}: '{}'".format(nu, l))

                        vregister = Vregister(level=level, name=name, offset=offset, path=path, fields=[])

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Vregister" in str(type(d)):
                                    vregister = d
                                    vregister.level, vregister.offset, vregister.path = level, offset, path
                            hier[-1].vregisters.append(vregister)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(vregister) 

                    # memory
                    elif re.search(r"^memory", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^memory\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^memory\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^memory\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^memory\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^memory\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^memory\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^memory\s+(\w+)", l): # name
                            match = re.search(r"^memory\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported memory format in line {}: '{}'".format(nu, l))

                        memory = Memory(level=level, name=name, offset=offset, path=path)

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Memory" in str(type(d)):
                                    memory = d
                                    memory.level, memory.offset, memory.path = level, offset, path
                            hier[-1].memories.append(memory)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(memory) 

                    # block
                    elif re.search(r"^block", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^block\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^block\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^block\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^block\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^block\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^block\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^block\s+(\w+)", l): # name
                            match = re.search(r"^block\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported block format in line {}: '{}'".format(nu, l))

                        block = Block(level=level, name=name, offset=offset, path=path, 
                            registers=[], vregisters=[], regfiles=[], memories=[])

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "Block" in str(type(d)):
                                    block = d
                                    block.level, block.offset, block.path = level, offset, path
                            hier[-1].blocks.append(block)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(block) 

                    # system
                    elif re.search(r"^system", l):
                        name, path, offset = '', '', '0'
                        if re.search(r"^system\s+(\w+)\s*\((.*)\)\s*@(\S+)", l): # name/path/offset
                            match = re.search(r"^system\s+(\w+)\s*\((.*)\)\s*@(\S+)", l)
                            name = match.group(1)
                            path = match.group(2)
                            offset = match.group(3)
                        elif re.search(r"^system\s+(\w+)\s*@(\S+)", l): # name/offset
                            match = re.search(r"^system\s+(\w+)\s*@(\S+)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^system\s+(\w+)\s*\((.*)\)", l): # name/path
                            match = re.search(r"^system\s+(\w+)\s*\((.*)\)", l)
                            name = match.group(1)
                            offset = match.group(2)
                        elif re.search(r"^system\s+(\w+)", l): # name
                            match = re.search(r"^system\s+(\w+)", l)
                            name = match.group(1)
                        else:
                            print("Error - unsupported system format in line {}: '{}'".format(nu, l))

                        system = System(level=level, name=name, offset=offset, path=path, 
                            blocks=[], systems=[])

                        if level: # sub level
                            # find from define list
                            for d in defs:
                                if d.name == name and "System" in str(type(d)):
                                    system = d
                                    system.level, system.offset, system.path = level, offset, path
                            hier[-1].systems.append(system)

                        if re.search(r"{\s*$", l): # new description
                            hier.append(system) 


# Only run the following code when this file is the main file being run
if __name__=='__main__':
    main()
