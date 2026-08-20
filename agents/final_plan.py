def create_final_plan(state):
    decisions = state["decisions"]

    return {
        "decisions": {
            **decisions,
            "final_plan": {
                "crop": decisions["crop_selection"],
                "planting": decisions["planting_schedule"],
                "irrigation": decisions["irrigation"],
                "fertilization": decisions["fertilization"],
                "harvesting": decisions["harvesting"],
                "livestock": decisions["livestock"],
                "labor": decisions["labor"],
                "land_expansion": decisions["land_expansion"],
                "market": decisions["market_trading"]
            }
        }
    }