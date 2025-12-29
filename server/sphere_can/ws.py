import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from sphere_can.state import STATE

async def readcan_ws(ws: WebSocket, bus: str):
    await ws.accept()
    backend = STATE.can_backends[bus]

    try:
        while True:
            frames = []

            while len(frames) < 32:
                try:
                    msg = backend.rx_queue.get_nowait()
                    frames.append({
                        "ts": msg.timestamp,
                        "bus": bus,
                        "id": hex(msg.arbitration_id),
                        "dlc": msg.dlc,
                        "data": msg.data.hex(),
                        "ext": msg.is_extended_id,
                    })
                except:
                    break

            if frames:
                try:
                    await ws.send_json(frames)
                except (WebSocketDisconnect, ConnectionClosedOK):
                    # Client closed cleanly
                    break

            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        pass

    finally:
        # Optional: explicit close for clarity
        try:
            await ws.close()
        except:
            pass

        print(f"[ws] readcan {bus} disconnected cleanly")
