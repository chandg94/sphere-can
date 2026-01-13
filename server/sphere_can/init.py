from sphere_can.can import CANBackend
from sphere_can.state import STATE
from sphere_can.relay import all_relays_off

def startup():
    # Software resources only
    STATE.can_backends["can0"] = CANBackend("can0")
    STATE.can_backends["can1"] = CANBackend("can1")

def shutdown():
    # Graceful teardown
    for backend in STATE.can_backends.values():
        backend.stop()

    for name, gen in list(STATE.generators.items()):
        try:
            gen["stop"].set()
            print(f"[shutdown] generator {name} stopped")
        except Exception as e:
            print(f"[shutdown] failed to stop generator {name}: {e}")

    STATE.generators.clear()

    try:
        all_relays_off()
    except Exception as e:
        print(f"[shutdown] relay shutdown failed: {e}")

    print("[shutdown] complete")
