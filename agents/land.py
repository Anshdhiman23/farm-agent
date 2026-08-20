def land_expansion_decision(state):
    current_land = state["land_acres"]
    capital = state["capital"]

    # Prototype assumptions
    additional_land = 5
    land_cost_per_acre = 80000
    expected_profit_per_acre = 42000

    total_land_cost = additional_land * land_cost_per_acre
    additional_profit = additional_land * expected_profit_per_acre

    if capital >= total_land_cost:
        payback_period = total_land_cost / additional_profit

        if payback_period <= 3:
            recommendation = "EXPAND"
        else:
            recommendation = "DO NOT EXPAND"
    else:
        payback_period = None
        recommendation = "DO NOT EXPAND - insufficient capital"

    return {
        "decisions": {
            **state["decisions"],
            "land_expansion": {
                "current_land_acres": current_land,
                "additional_land_acres": additional_land,
                "land_cost": total_land_cost,
                "expected_additional_profit": additional_profit,
                "payback_years": payback_period,
                "recommendation": recommendation
            }
        }
    }