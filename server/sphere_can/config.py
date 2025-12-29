import serial
from sphere_can.state import STATE

SER = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

def set_ecu(ecu: str, state: bool):
    cmd = f"{ecu}:{'ON' if state else 'OFF'}\n"
    SER.write(cmd.encode())

    with STATE.lock:
        STATE.ecu_state[ecu] = state
