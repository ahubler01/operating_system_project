# entities/gates.py
import threading
from queue import Empty
import time

class Gates(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                passenger = self.airport.gates_queues[self.id].get(timeout=self.airport.queue_timeout)
                print(f"{passenger.name} is boarding at gate {self.id}. Flight: {passenger.flight_nb}")
                time.sleep(2)
                self.airport.gates_queues[self.id].task_done()
            except Empty:
                pass