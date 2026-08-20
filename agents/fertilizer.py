def fertilizer_decision(state):
    n = state["soil_n"]
    p = state["soil_p"]
    k = state["soil_k"]
    crop = state["current_crop"]

    recommendations = []

    if n < 40:
        recommendations.append("Nitrogen fertilizer required")

    if p < 30:
        recommendations.append("Phosphorus fertilizer required")

    if k < 35:
        recommendations.append("Potassium fertilizer required")

    if not recommendations:
        recommendation = "No fertilizer required"
    else:
        recommendation = recommendations

    return {
        "decisions": {
            **state["decisions"],
            "fertilization": {
                "crop": crop,
                "soil_n": n,
                "soil_p": p,
                "soil_k": k,
                "recommendation": recommendation
            }
        }
    }