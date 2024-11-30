# entities/security.py

import threading
from queue import Empty
import random 
import time

class Security(threading.Thread):
    def __init__(self, 
                 id, 
                 airport
                ):
        
        super().__init__()
        self.id = id
        self.airport = airport

    def run(self):
        while not self.airport.simulation_end.is_set():
            try:
                passenger = self.airport.security_check_queue.get(timeout=1)
                self.airport.monitor.increment_usage("security", self.id)

                self.process_passenger(passenger) 
                
                self.airport.monitor.decrement_usage("security", self.id)
                self.airport.security_check_queue.task_done()                  
                
                if random.random() < passenger.p_shop:
                    self.airport.shops_queues[self.id % len(self.airport.shops_queues)].put(passenger)
                else:
                    self.airport.gates_queues[self.id % len(self.airport.gates_queues)].put(passenger)
            except Empty:
                pass

    def process_passenger(self, passenger):
        print(f"Security {self.id} serving {passenger.name}.")
        time_ = random.randint(1, 8)
        time.sleep(time_)
    
    def stop(self):
        """Stop the security thread."""
        self.is_active = False
        self.join()
        