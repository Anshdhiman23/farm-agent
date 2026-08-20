"""
Shared tools the agents can call.

These were previously hardcoded dicts buried inside individual agent
functions (e.g. `market.py` had a fixed `markets = {...}` dict). Pulling
them out as `@tool`-decorated functions means:
  1. An LLM-driven node can *choose* to call them (and could choose not
     to, or call them more than once) instead of having the lookup
     unconditionally baked into the function body.
  2. They're easy to swap for real APIs later (e.g. point
     `get_weather_forecast` at a real weather API, `get_market_prices`
     at a mandi price API) without touching agent logic.

For now the implementations are simulated / static, same as the data
they're replacing, but the *shape* of the call is what matters for the
conversion from "deterministic function" to "tool an agent can invoke."
"""

import random

from langchain_core.tools import tool


@tool
def get_weather_forecast(location: str = "farm") -> dict:
    """Get the short-term weather forecast (rainfall, temperature) for the farm's location.

    Use this before making an irrigation decision to check whether rain is
    expected before deciding to spend irrigation water.
    """
    # Simulated forecast. Replace with a real weather API call
    # (e.g. OpenWeatherMap, IMD) when available.
    return {
        "location": location,
        "next_3_day_rainfall_mm": round(random.uniform(0, 25), 1),
        "next_7_day_rainfall_mm": round(random.uniform(0, 60), 1),
        "avg_temperature_c": round(random.uniform(18, 34), 1),
        "humidity_pct": round(random.uniform(30, 85), 1),
    }


@tool
def get_market_prices(crop: str) -> dict:
    """Get current sale prices for a crop across nearby markets/mandis.

    Returns price per quintal and transport cost per market so the agent
    can weigh net price, not just headline price.
    """
    # Simulated mandi data with some randomness so repeated calls aren't
    # identical - closer to how a real price-feed would behave.
    base_prices = {"Wheat": 2200, "Rice": 2100, "Maize": 1850}
    base = base_prices.get(crop, 2000)

    markets = {
        "Local Market": {"price": base + random.randint(-50, 50), "transport": 0},
        "Market B": {"price": base + random.randint(100, 300), "transport": 100},
        "Market C": {"price": base + random.randint(50, 200), "transport": 50},
    }
    return {"crop": crop, "markets": markets}


@tool
def get_soil_health_report(soil_n: float, soil_p: float, soil_k: float, soil_ph: float) -> dict:
    """Get an interpreted soil health report from raw N-P-K and pH readings.

    Converts raw sensor numbers into qualitative flags (e.g. "nitrogen
    deficient") that are easier for the agent to reason about than raw
    numbers alone.
    """
    flags = []
    if soil_n < 40:
        flags.append("nitrogen_deficient")
    if soil_p < 20:
        flags.append("phosphorus_deficient")
    if soil_k < 30:
        flags.append("potassium_deficient")
    if not (5.5 <= soil_ph <= 7.5):
        flags.append("ph_out_of_ideal_range")

    return {
        "soil_n": soil_n,
        "soil_p": soil_p,
        "soil_k": soil_k,
        "soil_ph": soil_ph,
        "flags": flags,
        "overall": "needs_attention" if flags else "healthy",
    }


ALL_TOOLS = [get_weather_forecast, get_market_prices, get_soil_health_report]
