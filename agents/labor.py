def labor_decision(state):
    land = state["land_acres"]
    workers = state["available_workers"]
    crop = state["current_crop"]

    # Simple prototype assumption:
    # 1 worker can manage roughly 1.5 acres during peak operations
    required_workers = max(1, round(land / 1.5))

    shortage = max(0, required_workers - workers)

    if shortage > 0:
        recommendation = f"Hire {shortage} temporary workers"
    else:
        recommendation = "No additional workers required"

    return {
        "decisions": {
            **state["decisions"],
            "labor": {
                "crop": crop,
                "land_acres": land,
                "required_workers": required_workers,
                "available_workers": workers,
                "worker_shortage": shortage,
                "recommendation": recommendation
            }
        }
    }