import can
import threading
import queue
import random
import time

class CANBackend:
    def __init__(self, channel: str):
        self.rx_bus = can.interface.Bus(
            channel=channel,
            bustype="socketcan",
            receive_own_messages=True
        )
        self.tx_bus = can.interface.Bus(
            channel=channel,
            bustype="socketcan"
        )
        self.rx_queue = queue.Queue(maxsize=10000)
        # self.tx_queue = queue.Queue(maxsize=10000)
        self.running = True

        self.rx_worker = threading.Thread(
            target=self.rx_worker,
            daemon=True
        )
        self.rx_worker.start()

    def rx_worker(self):
        while self.running:
            msg = self.rx_bus.recv(timeout=0.01)
            if msg:
                try:
                    self.rx_queue.put_nowait(msg)
                except queue.Full:
                    pass
    # def _rx_worker(self):
    #     while self.running:
    #         msg = self.bus.recv(timeout=1.0)
    #         if msg:
    #             try:
    #                 self.rx_queue.put_nowait(msg)
    #             except queue.Full:
    #                 pass  # drop frames under load

    def send(self, msg: can.Message):
        self.tx_bus.send(msg)
    # def send(self, msg: can.Message):
    #     try:
    #         self.tx_queue.put_nowait(msg)
    #     except queue.Full:
    #         pass  # drop or log

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
