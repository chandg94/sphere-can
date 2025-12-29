import serial
from sphere_can.state import STATE

SER = None

def init_serial():
    global SER
    try:
        SER = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        print("[relay] Teensy connected")
    except Exception as e:
        SER = None
        print(f"[relay] Teensy not available: {e}")

def set_relay(ecu: str, on: bool):
    if SER is None:
        # Soft-fail: update state only
        with STATE.lock:
            STATE.ecu_state[ecu] = on
        print(f"[relay] (mock) {ecu} -> {'ON' if on else 'OFF'}")
        return

    cmd = f"{ecu}:{'ON' if on else 'OFF'}\n"
    SER.write(cmd.encode())

    with STATE.lock:
        STATE.ecu_state[ecu] = on
