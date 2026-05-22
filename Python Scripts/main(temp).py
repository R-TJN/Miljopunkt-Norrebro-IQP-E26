from dmrlookup import dmrlookup

licenseplates = ["DL21793","DP11563","test","CU45131","CM68188","DN91751","EL32831","BA66048","EF32068"]

results = dmrlookup(licenseplates)

for plate, data in results.items():
    print(f"{plate}: {data}")

total = len(results)
gas = sum(1 for d in results.values() if d["powertrain"] == "Benzin")
diesel = sum(1 for d in results.values() if d["powertrain"] == "Diesel")
electric = sum(1 for d in results.values() if d["powertrain"] == "El")
hydrogen = sum(1 for d in results.values() if d["powertrain"] == "Brint")
fgas = sum(1 for d in results.values() if d["powertrain"] == "F-Gas")
petroleum = sum(1 for d in results.values() if d["powertrain"] == "Petroleum")
ngas = sum(1 for d in results.values() if d["powertrain"] == "N-Gas")
methanol = sum(1 for d in results.values() if d["powertrain"] == "Metanol")
ethanol = sum(1 for d in results.values() if d["powertrain"] == "Ætanol")

print(f"Total: {total}")
print(f"Gas: {gas}")
print(f"Diesel: {diesel}")
print(f"Electric: {electric}")
print(f"Hydrogen: {hydrogen}")
print(f"F-Gas: {fgas}")
print(f"Petroleum: {petroleum}")
print(f"N-Gas: {ngas}")
print(f"Methanol: {methanol}")
print(f"Ethanol: {ethanol}")
