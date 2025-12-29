import json
import websocket
from typing import Optional
from sphere_can.config import api_base


def _format_frame(f):
    """
    Format frame in candump-like format
    """
    ts = f["ts"]
    bus = f["bus"]
    arb = f["id"].lower()
    data = f["data"]
    return f"({ts:.6f}) {bus} {arb}#{data}"


def _parse_filter_id(val: Optional[str]) -> Optional[int]:
    if val is None:
        return None
    return int(val, 16)


def readcan(
    can_interface: str,
    *,
    filter_id: Optional[str] = None,
    log: Optional[str] = None,
):
    """
    Read CAN frames from server (candump-style).

    Optionally log to file.
    """

    url = f"{api_base().replace('http', 'ws')}/ws/readcan/{can_interface}"
    ws = websocket.WebSocket()
    ws.connect(url)

    logfile = None
    if log:
        logfile = open(log, "a", buffering=1)
        print(f"[readcan] logging to {log}")

    filter_arb = _parse_filter_id(filter_id)

    try:
        while True:
            frames = json.loads(ws.recv())
            for f in frames:
                arb = int(f["id"], 16)

                if filter_arb is not None and arb != filter_arb:
                    continue

                line = _format_frame(f)

                # stdout
                print(line)

                # file
                if logfile:
                    logfile.write(line + "\n")

    except KeyboardInterrupt:
        print("\n[readcan] stopped by user")

    finally:
        try:
            ws.close()
        except:
            pass

        if logfile:
            logfile.close()
