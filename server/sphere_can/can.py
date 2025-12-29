import can
import threading
import queue
import random
import time

class CANBackend:
    def __init__(self, channel: str):
        self.channel = channel
        self.bus = can.interface.Bus(
            channel=channel,
            bustype="socketcan"
        )
        self.rx_queue = queue.Queue(maxsize=4096)
        self.running = True

        self.rx_thread = threading.Thread(
            target=self._rx_worker,
            daemon=True
        )
        self.rx_thread.start()

    def _rx_worker(self):
        while self.running:
            msg = self.bus.recv(timeout=1.0)
            if msg:
                try:
                    self.rx_queue.put_nowait(msg)
                except queue.Full:
                    pass  # drop frames under load

    def send(self, msg: can.Message):
        self.bus.send(msg)

    def stop(self):
        self.running = False


def run_cangen(req: dict, backend: CANBackend, stop_event: threading.Event):
    sent = 0

    while not stop_event.is_set():
        if req.get("random_id"):
            arb = random.randint(
                0, 0x1FFFFFFF if req.get("extended") else 0x7FF
            )
        else:
            arb = req["arbitration_id"]

        if req.get("random_data"):
            data = bytes(random.randint(0, 255) for _ in range(req["dlc"]))
        else:
            data = bytes(req["data"])

        msg = can.Message(
            arbitration_id=arb,
            data=data,
            is_extended_id=req.get("extended", False),
            dlc=req["dlc"],
        )

        try:
            backend.send(msg)
            sent += 1
        except can.CanOperationError:
            time.sleep(0.0001)
            continue

        if req.get("count") and sent >= req["count"]:
            break

        if req.get("interval_us", 0) > 0:
            time.sleep(req["interval_us"] / 1_000_000)
