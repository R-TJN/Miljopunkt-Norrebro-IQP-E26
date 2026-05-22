import time
import sys
from dmr import DMR

def dmrlookup(licenseplates):

    results = {}
    
    for plate in licenseplates:
        
        if plate in results:
            print(f"Skipping duplicate plate '{plate}', already looked up.")
            continue
        
        vehicle = DMR.get_by_plate(plate)
            
        if vehicle is None:
            print(f"Warning: plate '{plate}' not found, skipping.")
            continue
            
        results[plate] = {
            "powertrain": vehicle.propulsion,
            "vehicle_type": vehicle.type,
            "weight": vehicle.total_weight,
            "fuel_consumption": vehicle.fuel_consumption
        }
    return results

