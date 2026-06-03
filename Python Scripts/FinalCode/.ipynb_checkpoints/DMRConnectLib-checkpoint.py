import re
import sys
from dmr import DMR

def dmrlookup(plate):

    plate = plate.strip().upper()

    if not re.fullmatch(r'[A-Z]{2}[0-9]{5}', plate):
        return None

    try:
        print("Looking up vehicle info...")
        vehicle = DMR.get_by_plate(plate)
        #print(vars(vehicle))
    except (IndexError, Exception) as e:
        print(f"DMR failed for plate {plate}: {type(e).__name__}: {e}")
        return None

    if vehicle is None:
        return None

    return {
        "powertrain": vehicle.propulsion,
    }
