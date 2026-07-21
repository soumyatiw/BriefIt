import os

from langgraph.graph import StateGraph, END

from ai_engine.state import PipelineState
from ai_engine.nodes.ingest_node import ingest_node
from ai_engine.nodes.clean_node import clean_node
from ai_engine.nodes.embed_node import embed_node
from ai_engine.nodes.dedup_cluster_node import dedup_cluster_node
from ai_engine.nodes.sentiment_node import sentiment_node
from ai_engine.nodes.summarize_node import summarize_node
from ai_engine.nodes.translate_node import translate_node
from ai_engine.nodes.persist_node import persist_node


def has_new_articles(state: PipelineState) -> str:
    """Short-circuit to END if clean_node found no genuinely new articles."""
    return "embed" if len(state.get("clean_articles", [])) > 0 else END


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("clean", clean_node)
    graph.add_node("embed", embed_node)
    graph.add_node("dedup_cluster", dedup_cluster_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("translate", translate_node)
    graph.add_node("persist", persist_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "clean")
    graph.add_conditional_edges("clean", has_new_articles, {"embed": "embed", END: END})
    graph.add_edge("embed", "dedup_cluster")
    graph.add_edge("dedup_cluster", "sentiment")
    graph.add_edge("sentiment", "summarize")
    graph.add_edge("summarize", "translate")
    graph.add_edge("translate", "persist")
    graph.add_edge("persist", END)

    return graph


def compile_graph():
    graph = build_graph()
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/pipeline_checkpoints.db")

    if database_url.startswith("sqlite"):
        # Local development fallback — no Postgres required.
        import sqlite3
        from langgraph.checkpoint.sqlite import SqliteSaver
        conn = sqlite3.connect("data/pipeline_checkpoints.db", check_same_thread=False)
        checkpointer = SqliteSaver(conn)
    else:
        # Production — use the same Postgres DATABASE_URL as the rest of the app.
        # Render's connection string starts with 'postgres://'; psycopg2 needs
        # 'postgresql://', so normalise it here.
        from langgraph.checkpoint.postgres import PostgresSaver
        pg_url = database_url.replace("postgres://", "postgresql://", 1)
        checkpointer = PostgresSaver.from_conn_string(pg_url)
        checkpointer.setup()  # creates checkpoint tables on first run

    return graph.compile(checkpointer=checkpointer)
