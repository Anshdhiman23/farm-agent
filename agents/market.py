from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from tools import get_market_prices

_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

class MarketDecision(BaseModel):
    recommended_market: str
    net_price_per_quintal: float
    recommendation: str = Field(description="e.g. 'SELL AT <market>'")
    reasoning: str
    crop_choice_looks_unprofitable: bool = Field(
        description="Boolean only. True means the crop's market prices are poor "
            "enough that a different crop should have been planted. "
            "False means the crop is reasonably profitable. "
            "Must be true or false, never a string."
    )


def market_decision(state):
    crop = state["current_crop"]

    price_data = get_market_prices.invoke({"crop": crop})
    markets = price_data["markets"]

    # Deterministic calculation
    net_prices = {
        name: data["price"] - data["transport"]
        for name, data in markets.items()
    }

    best_market = max(net_prices, key=net_prices.get)
    best_net_price = net_prices[best_market]

    structured_llm = _llm.with_structured_output(MarketDecision)

    prompt = f"""You are a farm market/selling agent.

Crop being sold: {crop}

Market data:
{markets}

Net prices after transportation:
{net_prices}

The mathematically best market is:
{best_market}

Its net price is:
{best_net_price} per quintal.

Your task is to evaluate the market situation.

IMPORTANT:
1. recommended_market MUST be "{best_market}".
2. net_price_per_quintal MUST be {best_net_price}.
3. crop_choice_looks_unprofitable MUST be a boolean.
4. Use true or false, NOT strings.
5. Set crop_choice_looks_unprofitable to true only if the overall
   market prices are poor enough that another crop should have been
   planted instead.
6. Otherwise set it to false.
"""

    try:
        decision = structured_llm.invoke(prompt)

        result = {
            "recommended_market": decision.recommended_market,
            "net_price_per_quintal": decision.net_price_per_quintal,
            "recommendation": decision.recommendation,
            "reasoning": decision.reasoning,
            "crop_choice_looks_unprofitable":
                decision.crop_choice_looks_unprofitable,
        }

    except Exception as e:
        result = {
            "recommended_market": best_market,
            "net_price_per_quintal": best_net_price,
            "recommendation": f"SELL AT {best_market}",
            "reasoning": f"LLM unavailable ({e}); fell back to max net price.",
            "crop_choice_looks_unprofitable": False,
        }

    return {
        "decisions": {
            **state["decisions"],
            "market_trading": {
                "crop": crop,
                "markets": markets,
                "net_prices": net_prices,
                **result,
            },
        }
    }
