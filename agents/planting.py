from datetime import datetime, timedelta


def create_planting_schedule(state):
    crop = state["current_crop"]

    today = datetime.now()

    if crop == "Wheat":
        preparation_days = 5
        growth_days = 120
    elif crop == "Rice":
        preparation_days = 7
        growth_days = 120
    elif crop == "Maize":
        preparation_days = 5
        growth_days = 100
    else:
        preparation_days = 5
        growth_days = 110

    preparation_date = today
    sowing_date = today + timedelta(days=preparation_days)
    harvest_date = sowing_date + timedelta(days=growth_days)

    schedule = {
        "land_preparation": preparation_date.strftime("%Y-%m-%d"),
        "sowing": sowing_date.strftime("%Y-%m-%d"),
        "first_fertilizer": (sowing_date + timedelta(days=20)).strftime("%Y-%m-%d"),
        "irrigation_checkpoint": (sowing_date + timedelta(days=30)).strftime("%Y-%m-%d"),
        "harvest_preparation": (harvest_date - timedelta(days=10)).strftime("%Y-%m-%d"),
        "expected_harvest": harvest_date.strftime("%Y-%m-%d")
    }

    return {
        "planting_date": schedule["sowing"],
        "decisions": {
            **state["decisions"],
            "planting_schedule": schedule
        }
    }