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
builder.add_node("final_plan", create_final_plan)


builder.add_edge(START, "crop_selection")

builder.add_edge("crop_selection", "planting_schedule")
builder.add_edge("planting_schedule", "irrigation")
builder.add_edge("irrigation", "fertilization")
builder.add_edge("fertilization", "harvesting")
builder.add_edge("harvesting", "livestock")

builder.add_edge("harvesting", "livestock")
builder.add_edge("livestock", "labor")
builder.add_edge("labor", "land_expansion")
builder.add_edge("land_expansion", "market")
builder.add_edge("market", "final_plan")
builder.add_edge("final_plan", END)
graph = builder.compile()