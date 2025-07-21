from HumMod import createClient

# Create a client (represents one 'person')
client = createClient()

# Get the cardiac_output module
cardiac_output = client.getModule("CardiacOutput")

#print list of variables
vars = cardiac_output.vars()
print("Available variables:", vars)


#Calculate all
for i in vars:
    print(i,cardiac_output.calc(i))


result = cardiac_output.calc("StrokeVolume")


print("Calculated StrokeVolume:", result)


cardiac_output.set("StrokeVolume", 70)
#Example of manually setting value
print("Last Flow value:", cardiac_output.get("StrokeVolume"))