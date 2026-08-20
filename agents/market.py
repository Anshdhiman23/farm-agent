from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from tools import get_market_prices

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class MarketDecision(BaseModel):
    recommended_market: str
    net_price_per_quintal: float
    recommendation: str = Field(description="e.g. 'SELL AT <market>'")
    reasoning: str
    crop_choice_looks_unprofitable: bool = Field(
        description="True if prices for this crop are poor enough that a "
                     "different crop should have been chosen instead"
    )


def market_decision(state):
    crop = state["current_crop"]

    price_data = get_market_prices.invoke({"crop": crop})
    markets = price_data["markets"]

    net_prices = {name: data["price"] - data["transport"] for name, data in markets.items()}

    structured_llm = _llm.with_structured_output(MarketDecision)

    prompt = f"""You are a farm market/selling agent.

Crop being sold: {crop}
Market data (price and transport cost per quintal): {markets}
Net prices (price - transport): {net_prices}

Recommend the best market to sell at. Also judge whether the prices for
this crop are poor enough overall (e.g. all net prices unusually low)
that it would have been better to plant a different crop - set
crop_choice_looks_unprofitable accordingly."""

    try:
        decision = structured_llm.invoke(prompt)
        result = {
            "recommended_market": decision.recommended_market,
            "net_price_per_quintal": decision.net_price_per_quintal,
            "recommendation": decision.recommendation,
            "reasoning": decision.reasoning,
            "crop_choice_looks_unprofitable": decision.crop_choice_looks_unprofitable,
        }
    except Exception as e:
        best_market = max(net_prices, key=net_prices.get)
        result = {
            "recommended_market": best_market,
            "net_price_per_quintal": net_prices[best_market],
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
