import json
from graph import graph


with open("data/farm_data.json", "r") as f:
    farm_data = json.load(f)

result = graph.invoke(farm_data)

plan = result["decisions"]["final_plan"]

print("\n========== FINAL FARM PLAN ==========\n")

print("CROP")
print(plan["crop"])

print("\nPLANTING")
print(plan["planting"])

print("\nIRRIGATION")
print(plan["irrigation"])

print("\nFERTILIZATION")
print(plan["fertilization"])

print("\nHARVESTING")
print(plan["harvesting"])

print("\nLIVESTOCK")
print(plan["livestock"])

print("\nLABOR")
print(plan["labor"])

print("\nLAND EXPANSION")
print(plan["land_expansion"])

print("\nMARKET")
print(plan["market"])