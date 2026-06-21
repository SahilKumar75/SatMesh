from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import json
import os
from pathlib import Path

from api.graph_api import GraphAPI
from api.pipeline_runner import start_pipeline, get_status, stream_mock

app = FastAPI(title="SatMesh API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph_api = GraphAPI()

CITIES_JSON = Path("cities.json")
OUTPUTS_DIR = Path("outputs")


@app.get("/cities")
def list_cities():
    with open(CITIES_JSON) as f:
        cities = json.load(f)
    result = []
    for cid, cfg in cities.items():
        status = "not_run"
        summary_path = OUTPUTS_DIR / cid / "summary.json"
        running_path = OUTPUTS_DIR / cid / ".running"
        if running_path.exists():
            status = "running"
        elif summary_path.exists():
            status = "ready"
        result.append({"id": cid, "status": status, **cfg})
    return result


@app.get("/cities/{city_id}/status")
def city_status(city_id: str):
    summary_path = OUTPUTS_DIR / city_id / "summary.json"
    running_path = OUTPUTS_DIR / city_id / ".running"
    if running_path.exists():
        return {"status": "running"}
    if summary_path.exists():
        return {"status": "ready"}
    return {"status": "not_run"}


@app.get("/cities/{city_id}/graph")
def city_graph(city_id: str):
    geojson_path = OUTPUTS_DIR / city_id / "zones.geojson"
    if not geojson_path.exists():
        raise HTTPException(404, "Pipeline has not run for this city yet")
    with open(geojson_path) as f:
        return json.load(f)


@app.get("/cities/{city_id}/metrics")
def city_metrics(city_id: str):
    summary_path = OUTPUTS_DIR / city_id / "summary.json"
    if not summary_path.exists():
        raise HTTPException(404, "No metrics available yet")
    with open(summary_path) as f:
        return json.load(f)


@app.get("/cities/{city_id}/mask")
def city_mask(city_id: str):
    mask_path = OUTPUTS_DIR / city_id / "road_mask.png"
    if not mask_path.exists():
        raise HTTPException(404, "No mask available")
    return FileResponse(str(mask_path), media_type="image/png")


@app.post("/cities/{city_id}/run")
def run_pipeline(city_id: str, checkpoint: str = "checkpoints/segformer_india_v2.pth",
                 encoder: str = "mit_b4", mock: bool = False):
    if mock:
        return StreamingResponse(stream_mock(city_id), media_type="text/event-stream")
    return StreamingResponse(start_pipeline(city_id, checkpoint, encoder_name=encoder),
                             media_type="text/event-stream")


@app.post("/cities/{city_id}/reroute")
def reroute(city_id: str, body: dict):
    src = body.get("src")
    dst = body.get("dst")
    disabled = body.get("disabled_nodes", [])
    path, length = _graph_api.reroute(city_id, src, dst, disabled)
    return {"path": path, "length_m": length, "reachable": len(path) > 0}


@app.post("/cities/{city_id}/disable")
def disable_node(city_id: str, body: dict):
    node_id = body.get("node_id")
    result = _graph_api.disable_node(city_id, node_id)
    return result


@app.post("/cities/{city_id}/scenario")
def run_scenario(city_id: str, body: dict):
    scenario_type = body.get("type", "flood")
    params = body.get("params", {})
    return _graph_api.run_scenario(city_id, scenario_type, params)


app.mount("/", StaticFiles(directory="dashboard/web", html=True), name="dashboard")
