from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from tools import get_soil_health_report
load_dotenv()

_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

class CropDecision(BaseModel):
    recommended_crop: str = Field(description="One of: Wheat, Rice, Maize")
    confidence: float = Field(ge=0, le=1, description="0-1 confidence in this recommendation")
    reasoning: str = Field(description="Short explanation grounded in the inputs provided")


def _rule_based_scores(temperature: float, soil_ph: float, water: float) -> dict:
    """Kept as a deterministic baseline. The LLM sees these scores as one
    input among several rather than being the decision itself - this is
    what previously *was* the entire agent."""
    scores = {}

    wheat_score = 0
    if 15 <= temperature <= 25:
        wheat_score += 40
    if 6.0 <= soil_ph <= 7.5:
        wheat_score += 30
    if water >= 300000:
        wheat_score += 30
    scores["Wheat"] = wheat_score

    rice_score = 0
    if 20 <= temperature <= 35:
        rice_score += 40
    if 5.5 <= soil_ph <= 7.0:
        rice_score += 30
    if water >= 500000:
        rice_score += 30
    scores["Rice"] = rice_score

    maize_score = 0
    if 18 <= temperature <= 30:
        maize_score += 40
    if 5.5 <= soil_ph <= 7.5:
        maize_score += 30
    if water >= 250000:
        maize_score += 30
    scores["Maize"] = maize_score

    return scores


def select_crop(state):
    temperature = state["temperature"]
    soil_ph = state["soil_ph"]
    water = state["available_water_liters"]

    scores = _rule_based_scores(temperature, soil_ph, water)

    # The agent calls the soil tool to get a fuller picture than raw
    # N-P-K/pH numbers before reasoning about crop fit.
    soil_report = get_soil_health_report.invoke({
        "soil_n": state["soil_n"],
        "soil_p": state["soil_p"],
        "soil_k": state["soil_k"],
        "soil_ph": soil_ph,
    })

    structured_llm = _llm.with_structured_output(CropDecision)

    prompt = f"""You are a farm planning agent choosing the best crop to plant.

Conditions:
- Temperature: {temperature} C
- Available irrigation water: {water} liters
- Soil health report: {soil_report}
- Rule-of-thumb suitability scores (0-100, informational only, not authoritative): {scores}

Choose the crop (Wheat, Rice, or Maize) that best fits these conditions.
You are not bound by the suitability scores - override them if the soil
report flags something the score doesn't capture (e.g. a nutrient
deficiency that would hurt one crop more than another)."""

    try:
        decision = structured_llm.invoke(prompt)
        recommended_crop = decision.recommended_crop
        reasoning = decision.reasoning
        confidence = decision.confidence
    except Exception as e:
        # Fall back to the deterministic score if the LLM call fails
        # (e.g. no API key configured) so the graph still runs end-to-end.
        recommended_crop = max(scores, key=scores.get)
        reasoning = f"LLM unavailable ({e}); fell back to rule-based scoring."
        confidence = 0.5

    return {
        "current_crop": recommended_crop,
        "decisions": {
            **state["decisions"],
            "crop_selection": {
                "recommended_crop": recommended_crop,
                "confidence": confidence,
                "reasoning": reasoning,
                "rule_based_scores": scores,
                "soil_report": soil_report,
            },
        },
    }
