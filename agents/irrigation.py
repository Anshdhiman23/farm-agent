from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from tools import get_weather_forecast

_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

class IrrigationDecision(BaseModel):
    decision: str = Field(description="One of: IRRIGATE, WAIT, NO IRRIGATION")
    amount_mm: float = Field(ge=0, description="Irrigation amount in mm, 0 if not irrigating")
    reason: str = Field(description="Short explanation grounded in the inputs provided")


def irrigation_decision(state):
    moisture = state["soil_moisture"]
    water = state["available_water_liters"]

    # The agent calls a weather tool rather than trusting a static
    # `rainfall_forecast_mm` value baked into the input. If a forecast
    # was already supplied in state we still fetch a fresh one - this is
    # the node deciding to act (check reality) rather than only reading
    # what it's handed.
    forecast = get_weather_forecast.invoke({"location": "farm"})

    structured_llm = _llm.with_structured_output(IrrigationDecision)

    prompt = f"""You are a farm irrigation agent.

Conditions:
- Current soil moisture: {moisture}% (below 35% is considered low)
- Available irrigation water: {water} liters
- Weather forecast: {forecast}

Decide whether to IRRIGATE now, WAIT (moisture is low but rain is coming
soon), or take NO IRRIGATION action (moisture is already sufficient).
If you choose IRRIGATE, specify a reasonable amount in mm (typically
15-25mm for a light-to-moderate irrigation)."""

    try:
        decision = structured_llm.invoke(prompt)
        result = {
            "decision": decision.decision,
            "amount_mm": decision.amount_mm,
            "reason": decision.reason,
        }
    except Exception as e:
        # Deterministic fallback, equivalent to the original rule logic,
        # now using the tool-fetched forecast instead of a static field.
        rainfall = forecast["next_3_day_rainfall_mm"]
        if moisture < 35:
            if rainfall >= 10:
                result = {"decision": "WAIT", "amount_mm": 0,
                           "reason": f"LLM unavailable ({e}); rain expected, moisture low."}
            elif water > 0:
                result = {"decision": "IRRIGATE", "amount_mm": 18,
                           "reason": f"LLM unavailable ({e}); low moisture, no rain expected."}
            else:
                result = {"decision": "WAIT", "amount_mm": 0,
                           "reason": f"LLM unavailable ({e}); low moisture, no water available."}
        else:
            result = {"decision": "NO IRRIGATION", "amount_mm": 0,
                       "reason": f"LLM unavailable ({e}); moisture sufficient."}

    return {
        "decisions": {
            **state["decisions"],
            "irrigation": {**result, "forecast_used": forecast},
        }
    }
