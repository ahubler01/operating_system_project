# entities/shops.py

import threading
from queue import Empty
import time 
import random 

class Shops(threading.Thread):
    def __init__(self, 
                 id, 
                 airport
                ):
        
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active and not self.airport.simulation_end.is_set():
            try:
                passenger = self.airport.shops_queues[self.id].get(timeout=1)
                self.airport.monitor.increment_usage("shops", self.id)

                self.process_passenger(passenger)

                gate_queue = self.airport.gates_queues[passenger.gate_id]
                gate_queue.put(passenger)
                self.airport.shops_queues[self.id].task_done()
                self.airport.monitor.decrement_usage("shops", self.id)
            
            except Empty:
                pass

    def process_passenger(self, passenger):
        print(f"Shop {self.id} serving {passenger.name}.")
        time_ = random.randint(1, 5)
        time.sleep(time_)
        
    def stop(self):
        """Stop the shop thread."""
        self.is_active = False
        self.join()
