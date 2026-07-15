from datetime import datetime

from ai_engine.graph import compile_graph


def main():
    app_graph = compile_graph()
    thread_id = f"manual-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
    print(f"Starting manual pipeline run ({thread_id})...")
    final_state = None
    
    for event in app_graph.stream({}, config={"configurable": {"thread_id": thread_id}}):
        for node_name, node_state in event.items():
            print(f" -> Finished node: {node_name}")
            final_state = node_state

    print("\nPipeline run complete.")
    if final_state:
        print("Final run_stats:", final_state.get("run_stats"))


if __name__ == "__main__":
    main()
