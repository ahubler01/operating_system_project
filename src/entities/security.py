# entities/security.py
import threading
from queue import Empty


class Security(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport

    def run(self):
        while not self.airport.simulation_end.is_set():
            try:
                passenger = self.airport.security_check_queue.get(timeout=1)
                print(f"Security {self.id} processing {passenger.name}.")
                threading.Event().wait(2)
                shop_queue = self.airport.shops_queues[self.id % len(self.airport.shops_queues)]
                shop_queue.put(passenger)            
            except Empty:
                pass
