from langgraph.graph import StateGraph

from app.graph.state import IngredientState
from app.agents.ingredient_agent import ingredient_agent

builder = StateGraph(
    IngredientState
)

builder.add_node(
    "ingredient_agent",
    ingredient_agent
)

builder.set_entry_point(
    "ingredient_agent"
)

builder.set_finish_point(
    "ingredient_agent"
)

graph = builder.compile()