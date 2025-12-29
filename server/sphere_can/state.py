from threading import Lock

class ServerState:
    def __init__(self):
        self.ecu_state = {
            "cummins": False,
            "ddec": False,
            "bendix": False,
        }
        self.can_backends = {}
        self.generators = {}
        self.lock = Lock()

STATE = ServerState()
