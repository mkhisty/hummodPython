from .module import Module

class HumModClient:
    def __init__(self):
        #stores all loaded modules
        self.modules = {}
        self.dt=1

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
    
    def displayModules(self):
        #Will display all modules which are triggered by calculating parameters
        print("Available modules:")
        for module_name, module in self.modules.items():
            print(f"  - {module_name}")



    def simulate(self, duration=10.0, timestep=1.0, apply=None):
        self.dt = timestep
        nsteps = int(duration / timestep)
        print(f"Simulating for {duration} minutes, timestep {timestep} min, {nsteps} steps.")
        results = []
        for step in range(nsteps):
            if(apply):
                apply(self, step)
            step_result = {}
            for module_name, module in self.modules.items():
                # Calculate all variables
                if hasattr(module, 'variables'):
                    for var in module.vars():
                        val = module.calc(var)
                        # Only store numerical values
                        if isinstance(val, (int, float)):
                            step_result[f"{module_name}.{var}"] = val
                # Calculate all definitions (blocks/calls)
                if hasattr(module, 'data') and 'definitions' in module.data:
                    for def_name in module.data['definitions']:
                        module.calc(def_name)
            results.append(step_result)
        print("Simulation complete.")
        return results
