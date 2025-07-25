import json
import os
import re
import logging

#All structures are of this class

class Module:
    def __init__(self, client, name):
        self.client = client #Parent Client
        self.name = name # Name of Structure
        self.variables = self._load_variables() #Variables and their calculation expressions
        
        self.values = {} #Last calculated/manually edited values
        self.user_set = set() # Track variables set by user

    def vars(self):
        #returns list of variables
        return list(self.variables.keys())

    def calc(self, var_name):
        #evaluates variables by going down the dependency chain if needed. Expression is compiled in preprocess
        expression = self.variables[var_name]
        result = eval(expression)

        self.values[var_name] = result
        self.user_set.discard(var_name)  # Remove from user_set if present
        return result


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

    def preprocess(self, expression):
        #
        identifiers = sorted(
            set(re.findall(r'[A-Za-z_][\w\-]*(?:\([^)]*\))?(?:\.[A-Za-z_][\w\-]*(?:\([^)]*\))?)*', expression)),#regex made with ai, to extract variable names.
                                                                                                                # Will manually remake in production
            key=len, reverse=True
        )

        eval_expression = expression

        for identifier in identifiers:
            if identifier.replace('.', '', 1).isdigit():
                continue
            if "." not in identifier: #local variable
                eval_expression = eval_expression.replace(identifier, f"self.get('{identifier}')")
            else: #intermodule variable
                eval_expression = eval_expression.replace(identifier, f"self.client.getVar('{identifier}')")
        return eval_expression

    def _load_variables(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'structures', f'{self.name}.json')

        with open(file_path, 'r') as f:
            return {k: self.preprocess(v) for k, v in json.load(f).items()}
