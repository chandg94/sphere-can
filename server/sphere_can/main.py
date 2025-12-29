from fastapi import FastAPI, WebSocket, HTTPException
from sphere_can.init import startup, shutdown
from sphere_can.ws import readcan_ws
from sphere_can.relay import set_relay
from sphere_can.status import get_status
from sphere_can.can import run_cangen
from sphere_can.state import STATE
import threading

app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

@app.websocket("/ws/readcan/{bus}")
async def ws_readcan(ws: WebSocket, bus: str):
    await readcan_ws(ws, bus)

@app.post("/can/send/{bus}")
def send_can(bus: str, req: dict):
    name = req.get("name")
    if not name:
        raise HTTPException(400, "generator name required")

    if name in STATE.generators:
        raise HTTPException(400, f"generator '{name}' already exists")

    if bus not in STATE.can_backends:
        raise HTTPException(404, f"bus '{bus}' not available")

    backend = STATE.can_backends[bus]
    stop_event = threading.Event()

    def runner():
        try:
            run_cangen(req, backend, stop_event)
        finally:
            STATE.generators.pop(name, None)

    t = threading.Thread(target=runner, daemon=True)
    t.start()

    STATE.generators[name] = {
        "thread": t,
        "stop": stop_event,
        "bus": bus,
    }

    return {"status": "started", "name": name, "bus": bus}

@app.post("/can/stop/{name}")
def stop_can(name: str):
    gen = STATE.generators.get(name)
    if not gen:
        raise HTTPException(404, f"generator '{name}' not found")

    gen["stop"].set()
    STATE.generators.pop(name, None)

    return {"status": "stopped", "name": name}

@app.post("/relay")
def relay(ecu: str, on: bool):
    set_relay(ecu, on)
    return {"ecu": ecu, "on": on}

@app.get("/status")
def status():
    return get_status()
