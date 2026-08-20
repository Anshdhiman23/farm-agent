from langgraph.graph import StateGraph, START, END

from state import FarmState
from agents.crop import select_crop
from agents.planting import create_planting_schedule
from agents.irrigation import irrigation_decision
from agents.fertilizer import fertilizer_decision
from agents.harvest import harvest_decision
from agents.livestock import livestock_decision
from agents.labor import labor_decision
from agents.land import land_expansion_decision
from agents.market import market_decision
from agents.final_plan import create_final_plan


def route_after_harvest(state):
    """Conditional routing: skip the livestock node entirely if the farm
    has no livestock, instead of always visiting it like the old fixed
    linear pipeline did."""
    if state.get("livestock_count", 0) > 0:
        return "livestock"
    return "labor"


def replan_guard(state):
    """Control node: decides whether the crop choice should be revisited,
    based on the market agent's own judgment (crop_choice_looks_unprofitable)
    rather than a hardcoded rule. Caps re-planning at one loop so this
    can't cycle forever."""
    market = state["decisions"].get("market_trading", {})
    unprofitable = market.get("crop_choice_looks_unprofitable", False)
    replan_count = state.get("replan_count", 0)
    should_replan = unprofitable and replan_count == 0

    updates = {
        "decisions": {
            **state["decisions"],
            "replan_guard": {
                "should_replan": should_replan,
                "replan_count": replan_count + (1 if should_replan else 0),
            },
        }
    }
    if should_replan:
        updates["replan_count"] = replan_count + 1
    return updates


def route_after_market(state):
    return "crop_selection" if state["decisions"]["replan_guard"]["should_replan"] else "final_plan"


builder = StateGraph(FarmState)

builder.add_node("crop_selection", select_crop)
builder.add_node("planting_schedule", create_planting_schedule)
builder.add_node("irrigation", irrigation_decision)
builder.add_node("fertilization", fertilizer_decision)
builder.add_node("harvesting", harvest_decision)
builder.add_node("livestock", livestock_decision)
builder.add_node("labor", labor_decision)
builder.add_node("land_expansion", land_expansion_decision)
builder.add_node("market", market_decision)
builder.add_node("replan_guard", replan_guard)
builder.add_node("final_plan", create_final_plan)

builder.add_edge(START, "crop_selection")
builder.add_edge("crop_selection", "planting_schedule")
builder.add_edge("planting_schedule", "irrigation")
builder.add_edge("irrigation", "fertilization")
builder.add_edge("fertilization", "harvesting")

# Conditional: only visit the livestock node if the farm actually has
# livestock, instead of unconditionally running it every time.
builder.add_conditional_edges(
    "harvesting",
    route_after_harvest,
    {"livestock": "livestock", "labor": "labor"},
)
builder.add_edge("livestock", "labor")

builder.add_edge("labor", "land_expansion")
builder.add_edge("land_expansion", "market")
builder.add_edge("market", "replan_guard")

# Conditional loop-back: if the market agent judges the crop choice was
# poor given real prices, route back to crop_selection to re-plan.
# replan_guard caps this at a single loop.
builder.add_conditional_edges(
    "replan_guard",
    route_after_market,
    {"crop_selection": "crop_selection", "final_plan": "final_plan"},
)

builder.add_edge("final_plan", END)

graph = builder.compile()
