#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

import os
import traceback
from copy import deepcopy

class Signal(object):
    """docstring for Signal"""
    def __init__(self, name, sigType, width, initial):
        super(Signal, self).__init__()
        self.name = name
        self.sigType = sigType
        self.width = width
        self.initial = initial

    def __str__(self):
        widthStr = ''
        if self.width > 1:
            widthStr = '('+str(self.width-1)+' downto 0)'
        initStr = ''
        if self.initial != '':
            initStr = ' := '+ self.initial
        s = '\tsignal '+self.name+' : '+self.sigType+widthStr+initStr+';\n'
        return s

class Constant(object):
    """docstring for Constant"""
    def __init__(self, name, constType, width, value):
        super(Constant, self).__init__()
        self.name = name
        self.constType = constType
        self.width = width
        self.value = value

    def __str__(self):
        widthStr = ''
        if self.width > 1:
            widthStr = '('+str(self.width-1)+' downto 0)'
        s = '\tconstant '+self.name+' : '+self.constType+widthStr+' := '+ self.value+';\n'
        return s

class Port(object):
    """docstring for Port"""
    def __init__(self, name, direction, portType, width):
        super(Port, self).__init__()
        self.name = name
        self.direction = direction
        self.portType = portType
        self.width = width

    def __str__(self):
        widthStr = ''
        if int(self.width) > 1:
            widthStr = '('+str(int(self.width)-1)+' downto 0)'
        return self.name + '\t: ' + self.direction + ' ' + self.portType + widthStr


class Entity(object):
    """docstring for Entity"""
    def __init__(self, typeName):
        super(Entity, self).__init__()
        self.typeName = typeName
        self.ports = []
        self.portmap = dict({})

    def __str__(self):
        s = '\nentity ' + self.typeName + ' is\n'
        s+= self.printPortDecl()
        s+= '\nend entity;\n'
        return s

    def addPort(self,name,direction='in',portType='std_logic',width=1):
        name = "".join(name.split())
        direction = "".join(direction.split())
        portType = portType.strip()
        if (direction != 'in') and (direction != 'out') and (direction != 'inout'):
            traceback.print_stack()
            raise SystemExit(__file__ +': Error: invalid port direction in component: ' + self.typeName + ', for signal: ' + name)
        self.ports.append((name,Port(name, direction, portType, width)))

    def bindPort(self,portName,signalName):
        portName = "".join(portName.split()) # Removes all whitespace
        signalName = "".join(signalName.split()) # Removes all whitespace
        for name, port in self.ports:
            if portName == name:
                self.portmap[portName] = signalName
                return

        traceback.print_stack()
        raise SystemExit(__file__ +': Error: invalid port for binding component: ' + self.typeName + ', for port: ' + portName + ', for signal: ' + signalName + '\n' + str(self.ports))

    def printPortDecl(self):
        s = ''
        if len(self.ports) > 0:
            s = '\tport(\n\t\t'
            s+= ';\n\t\t'.join(str(port) for name, port in self.ports)
            s+= '\n\t);\n'
        return s

    def printInstance(self,label,fromWork):
        work = ''
        if fromWork:
            work = 'entity work.'
        connection = []
        s = '\n\t' + label + ' : ' + work + self.typeName + ' port map(\n\t\t'
        for name, port in self.ports:
            if port.name in self.portmap:
                connection.append(port.name + '\t=>\t' + self.portmap[port.name])
            else:
                con = 'open'
                if port.direction == 'in':
                    if port.width == 1:
                        con = "'0'"
                    else:
                        con = "(others => '0')"
                connection.append(port.name + '\t=>\t' + con)
        s+= ',\n\t\t'.join(connection)
        s+= '\t);\n'
        return s

    def printCompDecl(self):
        s = '\n\tcomponent ' + self.typeName + ' is\n'
        s+= self.printPortDecl()
        s+= '\n\tend component;\n'
        return s


class Architecture(object):
    """docstring for Architecture"""
    def __init__(self, entityName, name):
        super(Architecture, self).__init__()
        self.entityName = entityName
        self.name = name
        self.declaration = []
        self.body = []
        self.labels = []
        self.fromWork = []

    def __str__(self):
        s = '\narchitecture ' + self.name + ' of ' + self.entityName + ' is\n'
        s+= self.printDecl()
        s+= '\nbegin\n'
        s+= self.printBody()
        s+= '\nend ' + self.name + ';\n'
        return s

    def declSignal(self,name, sigType, width = 1, initial = ''):
        name = "".join(name.split())
        sigType = sigType.strip()
        self.declaration.append(Signal(name, sigType, width, initial))

    def declConstant(self,name, constType, width, value):
        name = "".join(name.split())
        constType = constType.strip()
        self.declaration.append(Constant(name, constType, width, value))

    def decl(self,s):
        self.declaration.append(s)

    def declComp(self,comp):
        self.declaration.append(comp)

    def printDecl(self):
        s = ''
        for d in self.declaration:
            if isinstance(d, Component):
                s+=d.entity.printCompDecl()
            elif isinstance(d, Signal):
                s+=str(d)
            elif isinstance(d, Constant):
                s+=str(d)
            elif isinstance(d, str):
                s+=d
        return s

    def instComp(self,comp,label,fromWork=False):
        self.body.append(deepcopy(comp.entity))
        self.labels.append(label)
        self.fromWork.append(fromWork)

    def addToBody(self,s):
        self.body.append(s)
        self.labels.append('')
        self.fromWork.append(False)

    def printBody(self):
        s = ''
        for i in range(0,len(self.body)):
            b = self.body[i]
            if isinstance(b, str):
                s+= b
            elif isinstance(b,Entity):
                s+= b.printInstance(self.labels[i],self.fromWork[i])
            else:
                pass
        return s


class Component(object):
    """docstring for Component"""
    def __init__(self, typeName):
        super(Component, self).__init__()
        typeName = "".join(typeName.split())
        self.entity = Entity(typeName)
        self.arch = Architecture(typeName,'struct')
        self.libraries = dict({})

    def addPackage(self,lib,package):
        lib = "".join(lib.split())
        package = "".join(package.split())
        if lib not in self.libraries:
            self.libraries[lib] = []
        self.libraries[lib].append(package)

    def writeLibraries(self):
        s = ''
        for lib in self.libraries.keys():
            s+= '\nlibrary ' + lib + ';\n'
            for package in self.libraries[lib]:
                s+= 'use '+lib+'.'+package+'.all;\n'
        return s

    def writeComp(self,filename):
        f = open(filename, 'w')
        f.write(self.writeLibraries())
        f.write(str(self.entity))
        f.write(str(self.arch))
        f.close()
