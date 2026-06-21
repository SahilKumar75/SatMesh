import json
import time
from pathlib import Path


_running: dict[str, bool] = {}


def start_pipeline(city_id: str, checkpoint: str, encoder_name: str = "mit_b4"):
    import sys
    sys.path.insert(0, ".")
    from src.pipeline import run_pipeline

    out_dir = Path("outputs") / city_id
    out_dir.mkdir(parents=True, exist_ok=True)
    running_flag = out_dir / ".running"
    running_flag.touch()

    try:
        for event in run_pipeline(city_id, checkpoint, encoder_name=encoder_name):
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        if running_flag.exists():
            running_flag.unlink()


def stream_mock(city_id: str):
    log_path = Path("outputs") / city_id / "pipeline_log.jsonl"
    if log_path.exists():
        with open(log_path) as f:
            events = [json.loads(line) for line in f if line.strip()]
        for ev in events:
            time.sleep(0.8)
            yield f"data: {json.dumps(ev)}\n\n"
    else:
        steps = [
            ("loading_model", 0),
            ("segmenting", 10),
            ("skeletonizing", 25),
            ("healing", 38),
            ("elevation", 48),
            ("criticality", 58),
            ("zones", 75),
            ("apls", 85),
            ("eval", 92),
            ("done", 100),
        ]
        for step, pct in steps:
            time.sleep(0.9)
            ev = {"step": step, "pct": pct, "ts": time.time(), "mock": True}
            yield f"data: {json.dumps(ev)}\n\n"


def get_status(city_id: str) -> str:
    running_flag = Path("outputs") / city_id / ".running"
    summary = Path("outputs") / city_id / "summary.json"
    if running_flag.exists():
        return "running"
    if summary.exists():
        return "ready"
    return "not_run"
