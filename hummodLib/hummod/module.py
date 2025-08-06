
import json
import os
import re
import logging
from scipy.interpolate import CubicSpline



#All structures are of this class

class Module:
    def __init__(self, client, name):
        self.client = client #Parent Client
        self.name = name # Name of Structure
        self.data = self._load_data() #Load the JSON data
        self.variables = self._process_variables() #Variables and their calculation expressions
        
        self.values = {} #Last calculated/manually edited values
        self.user_set = set()

    def curve(self, p1_x, p1_y, p1_slope, p2_x, p2_y, p2_slope, x):
        xs = [p1_x, p2_x]
        ys = [p1_y, p2_y]
        bc_type = ((1, p1_slope), (1, p2_slope))
        cs = CubicSpline(xs, ys, bc_type=bc_type)
        return float(cs(x))
    
    def vars(self):
        #returns list of variables
        return list(self.variables.keys())

    def display(self):
        #Will display variables/blocks contents
        print(f"Module: {self.name}")
        if 'variables' in self.data:
            print("  Variables:")
            for var_name, var_data in self.data['variables'].items():
                print(f"    {var_name}: {var_data}")
        if 'definitions' in self.data:
            print("  Definitions:")
            for def_name, def_data in self.data['definitions'].items():
                print(f"    {def_name}: {def_data}")
        if 'functions' in self.data:
            print("  Functions:")
            for func_name, func_data in self.data['functions'].items():
                print(f"    {func_name}: {func_data}")

    def calc(self, var_name):
        if var_name in self.user_set:
            return self.values.get(var_name)

        if 'variables' in self.data and var_name in self.data['variables']:
            var_info = self.data['variables'][var_name]
            value = var_info.get('value', None)
            if value is not None:
                # If value is a number or string, return it
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return value
            # If value is null, check if there's a function to compute it
            if 'functions' in self.data and var_name in self.data['functions']:
                # Try to get arguments from definitions
                arg_expr = self._get_function_args_from_definitions(var_name)
                if arg_expr:
                    func_name, args = arg_expr
                    # Recursively calc for args (vars/blocks)
                    arg_vals = []
                    for arg in args:
                        if arg in self.data.get('variables', {}):
                            arg_vals.append(self.calc(arg))
                        elif arg in self.data.get('definitions', {}):
                            arg_vals.append(self.calc(arg))
                        else:
                            arg_vals.append(arg)
                    return self._apply_function(func_name, arg_vals)
            # If value is null, no function, but is in definitions, fall through to definitions logic below
        if 'definitions' in self.data:
            defs = self.data['definitions']
            if var_name in defs:
                definition = defs[var_name]
                # If definition is a dict, handle CALLS, function calls, and string definitions in any combination
                if isinstance(definition, dict):
                    result = None
                    for key, expr in definition.items():
                        if key == 'CALLS' and isinstance(expr, list):
                            for call in expr:
                                module_name, def_name = call.split('.')
                                module = self.client.getModule(module_name)
                                module.calc(def_name)
                        else:
                            result = expr
                    return result

#        if var_name in self.data['functions']: Not Sure if i need this
#            return self._apply_function(var_name, [])

        return None

    def set(self, var_name, value):
        #Manually set variable
        self.values[var_name] = value
        self.user_set.add(var_name)

    def get(self, var_name):
        #Returns user-set value, or calculates it if not set by user
        if var_name in self.user_set:
            return self.values.get(var_name)
        else:
            return self.calc(var_name)

    def _load_data(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'structures', f'{self.name}.json')

        with open(file_path, 'r') as f:
            return json.load(f)

    def _process_variables(self):
        # Process variables from the loaded data
        variables = {}
        if 'variables' in self.data:
            for var_name, var_data in self.data['variables'].items():
                if 'value' in var_data:
                    variables[var_name] = var_data['value']
        return variables

    def _parse_function_call(self, expr):
        # Parses expressions like 'Effect [ Area ]' -> ('Effect', ['Area'])
        match = re.match(r'([A-Za-z0-9_\-]+)\s*\[([^\]]*)\]', expr)
        if match:
            func_name = match.group(1).strip()
            args = [a.strip() for a in match.group(2).split(',') if a.strip()]
            return func_name, args
        return expr.strip(), []

    def _get_function_args_from_definitions(self, var_name):
        # Looks for a definition that calls this function
        if 'definitions' in self.data:
            for def_name, def_val in self.data['definitions'].items():
                if isinstance(def_val, dict):
                    for key, expr in def_val.items():
                        func_name, args = self._parse_function_call(expr)
                        if func_name == var_name:
                            return func_name, args
                elif isinstance(def_val, str):
                    func_name, args = self._parse_function_call(def_val)
                    if func_name == var_name:
                        return func_name, args
        return None

    def _apply_function(self, func_name, args):
        # Get the function definition
        func_def = self.data['functions'][func_name]
        if func_def and func_def.startswith('<CURVE(') and func_def.endswith(')>'):
            # Parse CURVE expression: <CURVE((0.0,1.0,0.0),(3.3,0.0,0.0))>
            curve_content = func_def[7:-2]  # Remove '<CURVE(' and ')>'
            # Parse the two tuples
            tuples = curve_content.split('),(')
            if len(tuples) == 2:
                tuple1 = tuples[0].strip('(')
                tuple2 = tuples[1].strip(')')
                coords1 = [float(x.strip()) for x in tuple1.split(',')]
                coords2 = [float(x.strip()) for x in tuple2.split(',')]
                # Get the x value from args (should be the first argument)
                x_value = args[0] if args else 0.0
                # If x_value is not a float, try to convert
                try:
                    x_value = float(x_value)
                except Exception:
                    x_value = 0.0
                return self.curve(float(coords1[0]), float(coords1[1]), float(coords1[2]),
                           float(coords2[0]), float(coords2[1]), float(coords2[2]), x_value)
        # For other function types like DFQs, return 0 for now
        return 0
