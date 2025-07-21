# HumMod Python Port

This is a project which will convert HumMod, the comprehensive physiology model into a python library and allow it to integrate into future projects.

## The Design Goal

Ultimately, this library will allow HumMod to be used as such:

```python

import HumMod

port = HumMod.createClient() #Every module accesed through the same client is interdependent.
                             #One client represents one "person".

cardiacOutput = port.getModule("cardiac_output")

vars = cardiacOutput.vars() #Returns list of available member variable names.
flow = cardiacOutput.calc(vars[0]) #Calculates the variable 


#Sets the value of the variable, and the calculations of all other variables will use this value.
#Is rewritten when .calc() is used again.
cardiacOutput.set(vars[1],7)
print(cardiacOutput.get(vars[1])) # Prints 7, .get() returns the last calculated value and 
#does not guarantee any new update.
```


Alternatively, metaprogramming is an option that would allow the user to access the variables using the variable names directly, rather than as strings. (For example: ```cardiacOuput.calcFlow()``` as oppsed to ```cardiacOutput.calc("flow")```. Given that this maybe used in a simulation, which may require the user to manipulate thousands of variables which wont be hardcoded, the string based approach seems to be better.

## Engineering Method

HumMod is a vast and intricate network of variables. Initially, I considered a method in which every structure would be its own python object, and be a node in the complete HumMod graph, and that every change in any node would propogate throughout the graph, resulting in a ready-to-use and up-to-date state of all variables at all times. 

However, this involves a large computational overhead for tasks that may not require a vast proportion of HumMod. Therefore, to make this more meory efficient, another method would be to only load classes into memory that either
* The user deliberately instantiated
* Are required for the calculation of a variable the user has requested

For instance, in the example code, only cardiacOutput would initially be loaded into memory. However, when the user attempts to calculate a variable, ```LeftHeartPumping-Pumping``` is loaded into memory. If the user tries to access ```LeftHeartPumping-Pumping```  as a class directly through ```getModule```, the library would return the same class that was loaded into memory. This way, only the classes that are needed take up resources. This method will slow down runtime performance due to reading from disk.


I will experiment with both, the eager and lazy methods, to find a sweet point for the tradeoff between memory and runtime performance.

To allow the python library to convert the ```.des``` schema into python objects, I will be using an xml parser to first turn all XML scripts into json which would server as a configuration packet for a certain structure.

## Current Progress and next steps.
Currently, I have made a proof-of-concept library (with lazy loading) and only translated placeholder structures.
If the design goal is agreed upon then within the coming week I will:
* Translate all structures
* Detect & solve circular dependencies
* Test lazy loading scheme across real, long structure chains instead of the placeholders.  
To run, run ```test.py``` in the same directory as ```HumMod```


