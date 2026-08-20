def irrigation_decision(state):
    moisture = state["soil_moisture"]
    rainfall = state["rainfall_forecast_mm"]
    water = state["available_water_liters"]

    if moisture < 35:
        if rainfall >= 10:
            decision = "WAIT"
            amount = 0
            reason = "Soil moisture is low, but significant rainfall is expected."
        elif water > 0:
            decision = "IRRIGATE"
            amount = 18
            reason = "Soil moisture is low and sufficient rainfall is not expected."
        else:
            decision = "WAIT"
            amount = 0
            reason = "Soil moisture is low but no irrigation water is available."
    else:
        decision = "NO IRRIGATION"
        amount = 0
        reason = "Soil moisture is sufficient."

    return {
        "decisions": {
            **state["decisions"],
            "irrigation": {
                "decision": decision,
                "amount_mm": amount,
                "reason": reason
            }
        }
    }