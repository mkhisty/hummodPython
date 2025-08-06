import json
import os
import shutil
from parser import Parser

parser = Parser()
dependencyMap = {}
missing_files = [] 



def addDependencies(file):
    dependencies = parser.getDependencies(file)
    dependencyMap[file] = {"dependencies":list(dependencies), "count":0}

for file in os.listdir("structs"):
    addDependencies(file)




visited = set()

def countDeps(file):
    if file in visited:
        return 0
    visited.add(file)
    deps = dependencyMap[file]['dependencies']
    count = len(deps)
    for dep in deps:
        dep_file = dep + ".DES"
        if dep_file in dependencyMap:
            count += countDeps(dep_file)
        else:
            missing_files.append(dep_file)
    return count

for i in dependencyMap:
    visited.clear()
    dependencyMap[i]['count'] = countDeps(i)





with open("map.json", "w") as f:
    json.dump(dependencyMap, f, indent=4)    
