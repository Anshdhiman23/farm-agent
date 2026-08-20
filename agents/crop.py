def select_crop(state):
    temperature = state["temperature"]
    soil_ph = state["soil_ph"]
    water = state["available_water_liters"]

    scores = {}

    # Wheat
    wheat_score = 0

    if 15 <= temperature <= 25:
        wheat_score += 40

    if 6.0 <= soil_ph <= 7.5:
        wheat_score += 30

    if water >= 300000:
        wheat_score += 30

    scores["Wheat"] = wheat_score

    # Rice
    rice_score = 0

    if 20 <= temperature <= 35:
        rice_score += 40

    if 5.5 <= soil_ph <= 7.0:
        rice_score += 30

    if water >= 500000:
        rice_score += 30

    scores["Rice"] = rice_score

    # Maize
    maize_score = 0

    if 18 <= temperature <= 30:
        maize_score += 40

    if 5.5 <= soil_ph <= 7.5:
        maize_score += 30

    if water >= 250000:
        maize_score += 30

    scores["Maize"] = maize_score

    recommended_crop = max(scores, key=scores.get)

    return {
        "current_crop": recommended_crop,
        "decisions": {
            "crop_selection": {
                "recommended_crop": recommended_crop,
                "scores": scores
            }
        }
    }