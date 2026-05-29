import re
import sys
from dmr import DMR

def dmrlookup(plate):

    plate = plate.strip().upper()

    if not re.fullmatch(r'[A-Z]{2}[0-9]{5}', plate):
        #print(f"Warning: plate '{plate}' is not a valid format, skipping.")
        return None

    vehicle = DMR.get_by_plate(plate)

    if vehicle is None:
        #print(f"Warning: plate '{plate}' not found.")
        return None

    return {
        "powertrain": vehicle.propulsion,
        "vehicle_type": vehicle.type,
        "weight": vehicle.total_weight,
        "fuel_consumption": vehicle.fuel_consumption
    }

