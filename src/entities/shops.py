# entities/shops.py
import threading
from queue import Empty
import time 

class Shops(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                passenger = self.airport.shops_queues[self.id].get(timeout=1)
                print(f"Shop {self.id} serving {passenger.name}.")
                time.sleep(2)
                gate_queue = self.airport.gates_queues[self.id % len(self.airport.gates_queues)]
                gate_queue.put(passenger)
                self.airport.shops_queues[self.id].task_done()
            except Empty:
                pass

    def process_passenger(self, passenger):
        print(f"Shop {self.id} processing {passenger.name}.")
        time.sleep(2)
