class Signal(object):
    """docstring for Signal"""
    def __init__(self, name, sigType, width, initial):
        super(Signal, self).__init__()
        self.name = name
        self.sigType = sigType
        self.width = width
        self.initial = initial

    def __str__(self):
        widthstr = ''
        if self.width > 1:
            widthstr = '('+str(self.width-1)+' downto 0)'
        s = '\n\tsignal '+self.name+' : '+sigType+widthstr' := initial;'
        return s

class Port(object):
    """docstring for Port"""
    def __init__(self, name, direction, portType, width):
        super(Port, self).__init__()
        self.name = name
        self.direction = Direction
        self.portType = portType
        self.width = width

    def __str__(self):
        widthstr = ''
        if self.width > 1:
            widthstr = '('+str(self.width-1)+' downto 0)'
        return self.name + '\t: ' + self.direction + ' ' + portType + widthstr


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

    def addPort(self,portName,portDirection,portType,portWidth):
        self.ports.append(Port(portName, portDirection, portType, portWidth))

    def bindPort(self,portName,signalName):
        self.portmap[portName] = signalName

    def printPortDecl(self):
        s = '\tport(\n\t\t'
        s+= ';\n\t\t'.join(str(port) for port in self.ports)
        s+= '\n\t);'
        return s

    def printInstance(self,label):
        s = '\n\t' + label + ' : ' + self.typeName + ' port map(\n\t\t'
        s+= ',\n\t\t'.join(port.name + '\t=>\t' + self.portmap[port.name] for port in ports)
        s+= '\t);'
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

    def __str__(self):
        s = '\narchitecture ' + self.name + ' of ' + self.entityName + ' is\n'
        s+= self.printDecl()
        s+= '\nbegin\n'
        s+= self.printBody()
        s+= '\nend architecture;\n'
        return s

    def printDecl(self):
        s = ''
        for d in self.declaration:
            if isinstance(d, Component):
                s+=d.entity.printCompDecl()
            elif isinstance(d, Signal):
                pass
        return s



    def printBody(self):
        s = ''
        for b in self.body:
            if isinstance(b, str):
                s+= b
            else:
                pass
        return s

    def declSignal(self):
        pass

    def declComp(self):
        pass

    def instComp(self):
        pass

    def addProcess(self):
        pass

    def addAsignment(self):
        pass

class Component(object):
    """docstring for Component"""
    def __init__(self, typeName):
        super(Component, self).__init__()
        self.entity = Entity(typeName)
        self.arch = Architecture(typeName,'struct')
        self.libraries = dict({})

    def addPackage(self,lib,package):
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
