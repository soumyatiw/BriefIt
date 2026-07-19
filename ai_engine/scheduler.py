"""
Pipeline scheduler.

Cadence:
- Ingests up to 60 fresh articles per hour
- Summarizes up to 10 stories per run (prevents Groq rate-limit exhaustion)
- Fires immediately on startup then every 60 minutes

The 60-minute window gives NLLB enough time to translate the new batch
before the next ingest run brings more articles in.
"""
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from ai_engine.graph import compile_graph

app_graph = compile_graph()


def run_pipeline_job():
    thread_id = f"run-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
    try:
        result = app_graph.invoke({}, config={"configurable": {"thread_id": thread_id}})
        stats = result.get("run_stats", {})
        print(
            f"[scheduler] '{thread_id}' OK — "
            f"ingested={stats.get('ingested', 0)} "
            f"summarized={stats.get('summarized', 0)} "
            f"translated={stats.get('translated', 0)}"
        )
    except Exception as e:
        print(f"[scheduler] pipeline run '{thread_id}' failed: {e}")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pipeline_job,
        "interval",
        minutes=60,          # one full run per hour
        id="briefit_pipeline",
        next_run_time=datetime.now(),  # fire immediately on startup
    )
    scheduler.start()
    return scheduler
