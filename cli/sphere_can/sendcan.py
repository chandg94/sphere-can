import requests
import time
import uuid
from typing import Optional
from sphere_can.config import api_base


def _parse_hex(val: Optional[str]) -> Optional[int]:
    if val is None:
        return None
    return int(val, 16)


def _parse_data(val: Optional[str], length: int) -> Optional[list[int]]:
    if val is None:
        return None
    if len(val) != length * 2:
        raise ValueError(
            f"Data length mismatch: expected {length} bytes, got {len(val)//2}"
        )
    return [int(val[i:i+2], 16) for i in range(0, len(val), 2)]


def sendcan(
    can_interface: str,
    *,
    extended: bool = False,
    gap_ms: float = 0.0,
    id: Optional[str] = None,
    data: Optional[str] = None,
    len: int = 8,
    random_id: bool = False,
    random_data: bool = False,
    count: Optional[int] = None,
):
    """
    CAN traffic generator (cangen-style).
    Ctrl+C stops transmission.
    """

    name = f"cli-{uuid.uuid4().hex[:8]}"

    arb_id = _parse_hex(id)
    payload = _parse_data(data, len)

    req = {
        "name": name,
        "arbitration_id": arb_id,
        "random_id": random_id or arb_id is None,
        "extended": extended,
        "data": payload,
        "random_data": random_data or payload is None,
        "dlc": len,
        "interval_us": gap_ms * 1000,
        "count": count,
    }

    start_url = f"{api_base()}/can/send/{can_interface}"
    stop_url = f"{api_base()}/can/stop/{name}"

    r = requests.post(start_url, json=req)
    r.raise_for_status()

    print(f"[sendcan] running (name={name}) — Ctrl+C to stop")

    try:
        # Block like cangen
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[sendcan] stopping…")
        try:
            requests.post(stop_url, timeout=2)
            print("[sendcan] stopped")
        except Exception as e:
            print(f"[sendcan] stop failed: {e}")
