import sqlite3

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from ai_engine.state import PipelineState
from ai_engine.nodes.ingest_node import ingest_node
from ai_engine.nodes.clean_node import clean_node
from ai_engine.nodes.embed_node import embed_node
from ai_engine.nodes.dedup_cluster_node import dedup_cluster_node
from ai_engine.nodes.sentiment_node import sentiment_node
from ai_engine.nodes.persist_node import persist_node


def has_new_articles(state: PipelineState) -> bool:
    return len(state.get("raw_articles", [])) > 0


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("clean", clean_node)
    graph.add_node("embed", embed_node)
    graph.add_node("dedup_cluster", dedup_cluster_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("persist", persist_node)
    # Day 8:  graph.add_node("summarize", summarize_node)
    # Day 9:  graph.add_node("translate", translate_node)

    graph.set_entry_point("ingest")
    graph.add_conditional_edges("ingest", has_new_articles, {True: "clean", False: END})
    graph.add_edge("clean", "embed")
    graph.add_edge("embed", "dedup_cluster")
    graph.add_edge("dedup_cluster", "sentiment")
    graph.add_edge("sentiment", "persist")
    graph.add_edge("persist", END)

    return graph


def compile_graph():
    graph = build_graph()
    conn = sqlite3.connect("data/pipeline_checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return graph.compile(checkpointer=checkpointer)
