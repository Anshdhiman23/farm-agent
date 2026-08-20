from datetime import datetime, timedelta


def harvest_decision(state):
    crop = state["current_crop"]
    planting_date = datetime.strptime(
        state["planting_date"], "%Y-%m-%d"
    )

    growth_periods = {
        "Wheat": 120,
        "Rice": 120,
        "Maize": 100
    }

    growth_days = growth_periods.get(crop, 110)

    harvest_date = planting_date + timedelta(days=growth_days)

    window_start = harvest_date
    window_end = harvest_date + timedelta(days=7)

    return {
        "decisions": {
            **state["decisions"],
            "harvesting": {
                "crop": crop,
                "expected_harvest": harvest_date.strftime("%Y-%m-%d"),
                "harvest_window": (
                    f"{window_start.strftime('%Y-%m-%d')} "
                    f"to {window_end.strftime('%Y-%m-%d')}"
                ),
                "recommendation": "Harvest during this window if weather conditions are favorable."
            }
        }
    }