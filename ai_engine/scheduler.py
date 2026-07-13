from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from ai_engine.graph import compile_graph

app_graph = compile_graph()


def run_pipeline_job():
    thread_id = f"run-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
    try:
        result = app_graph.invoke({}, config={"configurable": {"thread_id": thread_id}})
        print(f"[scheduler] pipeline run '{thread_id}' completed: {result.get('run_stats')}")
    except Exception as e:
        print(f"[scheduler] pipeline run '{thread_id}' failed: {e}")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pipeline_job,
        "interval",
        minutes=15,
        id="briefit_pipeline",
        next_run_time=datetime.now(),  # fire once immediately on startup, then every 15 min
    )
    scheduler.start()
    return scheduler
