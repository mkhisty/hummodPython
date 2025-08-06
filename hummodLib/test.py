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

