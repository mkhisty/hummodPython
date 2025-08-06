# Hummod Port


## Dependencies
<img width="1489" height="985" alt="image" src="https://github.com/user-attachments/assets/3a580b28-7dd0-4f32-929b-c32307d71354" />

What makes this project challenging is the sheer interconnectedness of Hummod. Map.py maps every dependency into map.json, and counts the total number of dependencies that it relies on. A common pattern is that the nodes have close to none or close to 2000 dependencies.
Relatively very non-trivial nodes are sparsely connected, however they are helpful for testing the simulation as they allow the library to be tested without the frustration of attempting to fix bugs in a module that relies on thousands of others.

## Simulation

```python
from hummod import createClient

client = createClient()

HeartValves = client.getModule("HeartValves")

HeartValves.display()  
HeartValves.calc("Parms")  
client.displayModules()  
TricuspidValve_Regurgitation = client.getModule("TricuspidValve-Regurgitation")  
TricuspidValve_Stenosis = client.getModule("TricuspidValve-Stenosis") 

print("Starting simulation for 10 minutes (1 min timestep)...")

results = []


def increment(client,i):
    client.getModule("TricuspidValve-Regurgitation").set("Area", i)



results=client.simulate(duration=10, timestep=1.0, apply=increment)


for i, step in enumerate(results):
    print(f"Step {i+1}: {step}")


import matplotlib.pyplot as plt
trace = [float(i["TricuspidValve-Regurgitation.Effect"]) for i in results]
plt.plot(range(len(trace)), trace, marker='o')
plt.xlabel('Step')
plt.ylabel('TricuspidValve-Regurgitation.Effect')
plt.grid(True)
plt.show()


```


<img width="591" height="461" alt="image" src="https://github.com/user-attachments/assets/4a0faa5b-dc7f-4a84-b471-3d4503832de6" />

