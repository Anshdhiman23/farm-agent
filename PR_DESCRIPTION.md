# Convert crop/irrigation/market nodes from rule engine to agentic reasoning

## What this changes

Every node in `graph.py` was a pure Python if-else / scoring function - no
LLM call, no tool use, no branching. This PR converts three representative
nodes (`crop_selection`, `irrigation`, `market`) into real agents, and
changes the graph itself from a fixed line into a graph with actual
branches and a re-planning loop.

### 1. `tools.py` (new)
Pulled the data that was hardcoded inside agent functions
(`market.py`'s fake market dict, the manually-input `rainfall_forecast_mm`
field) out into `@tool`-decorated functions: `get_weather_forecast`,
`get_market_prices`, `get_soil_health_report`. These are simulated for now
but are structured so a node can *choose* to call them, and so real APIs
can be swapped in later without touching agent logic.

### 2. `agents/crop.py`, `agents/irrigation.py`, `agents/market.py`
Each now:
- Calls a tool to ground itself in current conditions instead of only
  reading static input fields.
- Calls an LLM (`ChatOpenAI` + `with_structured_output`) to make the
  actual decision, with the old rule-based scoring kept as *context* fed
  to the LLM, not as the final answer. The LLM can override the score
  (e.g. crop.py explicitly tells it to override the score if the soil
  report flags something the score misses).
- Falls back to the original deterministic logic if the LLM call fails
  (e.g. no API key), so the graph still runs end-to-end during dev/demo
  without a key.
- Returns its reasoning in the decision dict, not just the decision, so
  the final plan is explainable.

### 3. `graph.py`
- Added `route_after_harvest`: conditionally skips the `livestock` node
  entirely if the farm has no livestock, instead of unconditionally
  visiting it every run.
- Added a `replan_guard` control node + `route_after_market`: the market
  agent can now flag `crop_choice_looks_unprofitable`, and the graph
  routes back to `crop_selection` to re-plan if so - a real loop, capped
  at one iteration via `replan_count` in state so it can't cycle forever.
- Fixed a duplicate `add_edge("harvesting", "livestock")` left over from
  the original code.

### 4. `state.py`
Added `replan_count` field used as the loop guard.

## What this does NOT change (yet)

`planting.py`, `fertilizer.py`, `harvest.py`, `livestock.py`, `labor.py`,
`land.py` are untouched - still deterministic. The same conversion
pattern (tool call for grounding -> LLM with structured output for the
decision -> deterministic fallback) applies directly to each; I left them
as-is to keep this PR reviewable rather than converting all ten nodes at
once. Happy to follow up with the rest in a second PR if this direction
looks right.

## Requires

`OPENAI_API_KEY` set in the environment (or `.env`, already supported via
`python-dotenv`) for the LLM path to run. Without it, every converted node
falls back to its original deterministic logic and the graph still
produces a full plan.

## How to verify

```bash
uv run app.py
```

Compare `decisions.crop_selection.reasoning`, `decisions.irrigation.reasoning`,
and `decisions.market_trading.reasoning` in the output - these are new and
show the LLM's grounded justification. To see the re-planning loop fire,
you can temporarily force `crop_choice_looks_unprofitable=True` in
`agents/market.py`'s fallback branch and confirm `crop_selection` runs
twice.
