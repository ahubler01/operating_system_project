# entities/counter.py

import threading
from queue import Empty
import time 
import random

class Counter(threading.Thread):
    def __init__(self, 
                 id, 
                 airport
                 ):
    
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                passenger = self.airport.counter_queue.get(timeout=1)
                self.airport.monitor.increment_usage("counters", self.id)
                
                self.process_passenger(passenger)
                
                self.airport.security_check_queue.put(passenger)
                self.airport.counter_queue.task_done()
                self.airport.monitor.decrement_usage("counters", self.id)
            except Empty:
                pass

    def process_passenger(self, passenger):
        print(f"Counter {self.id} serving {passenger.name}.")
        time_ = random.randint(1, 8)
        time.sleep(time_)
        
    def stop(self):
        """Stop the counter thread."""
        self.is_active = False
        self.join()  
        
