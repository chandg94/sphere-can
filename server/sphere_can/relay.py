from sphere_can.state import STATE

SER = None

# Try importing pyserial safely
try:
    import serial
    _HAS_PYSERIAL = hasattr(serial, "Serial")
except Exception:
    serial = None
    _HAS_PYSERIAL = False


def init_serial():
    """
    Lazily initialize the Teensy serial connection.
    This MUST NOT run at import time.
    """
    global SER

    import sys
    print("[relay] python:", sys.executable)
    print("[relay] serial file:", getattr(serial, "__file__", None))
    print("[relay] HAS_PYSERIAL:", _HAS_PYSERIAL)

    # Already initialized
    if SER is not None:
        return

    if not _HAS_PYSERIAL:
        print("[relay] pyserial not available; relay disabled")
        SER = None
        return

    try:
        SER = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        print("[relay] Teensy connected on /dev/ttyACM0")
    except Exception as e:
        SER = None
        print(f"[relay] Teensy not available: {e}")


def set_relay(ecu: str, on: bool):
    """
    Set ECU relay ON/OFF.
    Falls back to mock mode if Teensy is unavailable.
    """
    global SER

    # Ensure serial is initialized on first use
    if SER is None:
        init_serial()

    # Mock mode
    if SER is None:
        with STATE.lock:
            STATE.ecu_state[ecu] = on
        print(f"[relay] (mock) {ecu} -> {'ON' if on else 'OFF'}")
        return

    # Real hardware mode
    try:
        cmd = f"{ecu}:{'ON' if on else 'OFF'}\n"
        SER.write(cmd.encode())

        with STATE.lock:
            STATE.ecu_state[ecu] = on

        print(f"[relay] {ecu} -> {'ON' if on else 'OFF'}")
    except Exception as e:
        print(f"[relay] serial write failed: {e}")
        SER = None


def all_relays_off():

    global SER

    print("[relay] shutdown: forcing ALL relays OFF")

    # Ensure serial exists
    if SER is None:
        init_serial()

    # If still no serial, just update software state
    if SER is None:
        print("[relay] shutdown: no serial, updating software state only")
        with STATE.lock:
            for ecu in STATE.ecu_state:
                STATE.ecu_state[ecu] = False
        return

    # Send OFF to every known ECU
    try:
        with STATE.lock:
            ecus = list(STATE.ecu_state.keys())

        for ecu in ecus:
            try:
                cmd = f"{ecu}:OFF\n"
                SER.write(cmd.encode())
                print(f"[relay] shutdown: {ecu} -> OFF")

                with STATE.lock:
                    STATE.ecu_state[ecu] = False

            except Exception as e:
                print(f"[relay] shutdown: failed {ecu}: {e}")

        # Flush + close serial
        try:
            SER.flush()
        except Exception:
            pass

        try:
            SER.close()
            print("[relay] shutdown: serial closed")
        except Exception:
            pass

    finally:
        SER = None