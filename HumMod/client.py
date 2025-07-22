from .module import Module

class HumModClient:
    def __init__(self):

        #stores all loaded modules
        self.modules = {}

    def getModule(self, name):
        #returns cached module or loads a new one
        if name not in self.modules:
            self.modules[name] = Module(self, name)
        return self.modules[name]

    def getVar(self, name):
        #Used for inter-module variable refrences
        module_name, var_name = name.split(".")
        module = self.getModule(module_name)
        return module.get(var_name) 