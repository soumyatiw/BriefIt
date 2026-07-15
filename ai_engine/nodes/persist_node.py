from ai_engine.state import PipelineState


def persist_node(state: PipelineState) -> dict:
    # Article rows are written in embed_node; Story rows are written in
    # dedup_cluster_node. This node is the write point for Summary rows
    # starting Day 9 — intentional no-op today, not dead code.
    return {"run_stats": state.get("run_stats", {})}
