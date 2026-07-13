import sqlite3

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from ai_engine.state import PipelineState
from ai_engine.nodes.ingest_node import ingest_node
from ai_engine.nodes.clean_node import clean_node
from ai_engine.nodes.persist_node import persist_node


def has_new_articles(state: PipelineState) -> bool:
    """Conditional-edge function: short-circuit to END if a batch had zero
    new articles — no point running downstream stages on nothing."""
    return len(state.get("raw_articles", [])) > 0


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("clean", clean_node)
    graph.add_node("persist", persist_node)
    # Day 5:  graph.add_node("embed", embed_node)
    # Day 6:  graph.add_node("dedup_cluster", dedup_cluster_node)
    # Day 7:  graph.add_node("sentiment", sentiment_node)
    # Day 8:  graph.add_node("summarize", summarize_node)
    # Day 9:  graph.add_node("translate", translate_node)

    graph.set_entry_point("ingest")
    graph.add_conditional_edges("ingest", has_new_articles, {True: "clean", False: END})
    graph.add_edge("clean", "persist")
    # Day 5+: replace the line below — "clean" -> "embed" -> ... -> "persist" -> END
    graph.add_edge("persist", END)

    return graph


def compile_graph():
    graph = build_graph()
    conn = sqlite3.connect("data/pipeline_checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)
