from datetime import datetime

from ai_engine.graph import compile_graph


def main():
    app_graph = compile_graph()
    thread_id = f"manual-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
    result = app_graph.invoke({}, config={"configurable": {"thread_id": thread_id}})
    print("Pipeline run complete.")
    print("run_stats:", result.get("run_stats"))


if __name__ == "__main__":
    main()
