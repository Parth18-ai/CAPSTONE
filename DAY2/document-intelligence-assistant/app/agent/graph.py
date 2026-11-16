"""Wires the nodes together:

   retrieve -> (any good chunks?) -- no  --> not_found -> END
                                  -- yes --> decide_tool -> answer -> END
"""
from langgraph.graph import END, StateGraph

from app.agent import nodes
from app.agent.state import AgentState

g = StateGraph(AgentState)
g.add_node("retrieve", nodes.retrieve)
g.add_node("decide_tool", nodes.decide_tool)
g.add_node("answer", nodes.answer)
g.add_node("not_found", nodes.not_found)

g.set_entry_point("retrieve")
g.add_conditional_edges(
    "retrieve",
    lambda s: "decide_tool" if s["chunks"] else "not_found",
    {"decide_tool": "decide_tool", "not_found": "not_found"},
)
g.add_edge("decide_tool", "answer")
g.add_edge("answer", END)
g.add_edge("not_found", END)

agent = g.compile()


# Streaming version: runs retrieve -> (not_found | decide_tool) and STOPS before the answer,
# so the API can stream the answer text itself.
p = StateGraph(AgentState)
p.add_node("retrieve", nodes.retrieve)
p.add_node("decide_tool", nodes.decide_tool)
p.add_node("not_found", nodes.not_found)
p.set_entry_point("retrieve")
p.add_conditional_edges(
    "retrieve",
    lambda s: "decide_tool" if s["chunks"] else "not_found",
    {"decide_tool": "decide_tool", "not_found": "not_found"},
)
p.add_edge("decide_tool", END)
p.add_edge("not_found", END)

prep_agent = p.compile()
