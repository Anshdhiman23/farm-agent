def livestock_decision(state):
    animal_type = state["livestock_type"]
    count = state["livestock_count"]
    temperature = state["temperature"]

    feed_per_animal = {
        "cattle": 10,
        "goat": 2,
        "sheep": 2.5
    }

    water_per_animal = {
        "cattle": 50,
        "goat": 5,
        "sheep": 5
    }

    feed = feed_per_animal.get(animal_type, 5)
    water = water_per_animal.get(animal_type, 10)

    daily_feed = count * feed
    daily_water = count * water

    if temperature > 35:
        health_risk = "HIGH"
    elif temperature > 30:
        health_risk = "MEDIUM"
    else:
        health_risk = "LOW"

    return {
        "decisions": {
            **state["decisions"],
            "livestock": {
                "animal_type": animal_type,
                "count": count,
                "daily_feed_kg": daily_feed,
                "daily_water_liters": daily_water,
                "health_risk": health_risk,
                "recommendation": "Provide adequate feed and water and monitor animal health."
            }
        }
    }