import re
import sys
from dmr import DMR

def dmrlookup(plate):

    plate = plate.strip().upper()

    if not re.fullmatch(r'[A-Z]{2}[0-9]{5}', plate):
        return None

    try:
        vehicle = DMR.get_by_plate(plate)
    except (IndexError, Exception):
        return None

    if vehicle is None:
        return None

    return {
        "powertrain": vehicle.propulsion,
        "vehicle_type": vehicle.type,
        "weight": vehicle.total_weight,
        "fuel_consumption": vehicle.fuel_consumption
    }
