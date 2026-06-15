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
        # Identity & registration
        "make": vehicle.make,
        "model": vehicle.model,
        #"variant": vehicle.variant,
        #"vin": vehicle.vin,
        #"registration_number": vehicle.registration_number,
        #"vehicle_id": vehicle.vehicle_id,
        "type": vehicle.type,
        #"use": vehicle.use,

        # Dates
        #"first_registration": vehicle.first_registration,
        #"last_update": vehicle.last_update,

        # Body & physical
        #"color": vehicle.color,
        "model_year": vehicle.model_year,
        "body_type": vehicle.body_type,
        "doors": vehicle.doors,
        "total_weight": vehicle.total_weight,
        #"vehicle_weight": vehicle.vehicle_weight,
        #"tow_bar": vehicle.tow_bar,

        # Powertrain & emissions
        "powertrain": vehicle.propulsion,
        "cylinders": vehicle.cylinders,
        "fuel_consumption": vehicle.fuel_consumption,
        "particle_filter": vehicle.particle_filter,

        # Electric / hybrid
        "plugin_hybrid": vehicle.plugin_hybrid,
        "electricity_consumption": vehicle.electricity_consumption,
        "electric_range": vehicle.electric_range,
        "battery_capacity": vehicle.battery_capacity,
    }
