from sphere_can.can import CANBackend
from sphere_can.state import STATE
from sphere_can.relay import init_serial

def startup():
    STATE.can_backends["can0"] = CANBackend("can0")
    # STATE.can_backends["can1"] = CANBackend("can1")
    init_serial()

def shutdown():
    for backend in STATE.can_backends.values():
        backend.stop()
