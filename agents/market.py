def market_decision(state):
    crop = state["current_crop"]

    # Simulated market data
    markets = {
        "Local Market": {
            "price": 2200,
            "transport": 0
        },
        "Market B": {
            "price": 2450,
            "transport": 100
        },
        "Market C": {
            "price": 2350,
            "transport": 50
        }
    }

    net_prices = {}

    for market, data in markets.items():
        net_prices[market] = data["price"] - data["transport"]

    best_market = max(net_prices, key=net_prices.get)
    best_price = net_prices[best_market]

    return {
        "decisions": {
            **state["decisions"],
            "market_trading": {
                "crop": crop,
                "markets": markets,
                "net_prices": net_prices,
                "recommended_market": best_market,
                "net_price_per_quintal": best_price,
                "recommendation": f"SELL AT {best_market}"
            }
        }
    }