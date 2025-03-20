import json
file = open("./data/mc-a.json", "r")
data = json.load(file)
print(data) 
file.close()