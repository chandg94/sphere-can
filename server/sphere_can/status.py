from sphere_can.state import STATE

def get_status():
    with STATE.lock:
        return {
            "ecus": STATE.ecu_state,
            "can_interfaces": list(STATE.can_backends.keys()),
            "generators": list(STATE.generators.keys()),
        }
