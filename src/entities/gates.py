# entities/gates.py
import threading
from queue import Empty
import time
import random 


class Gates(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                passenger = self.airport.gates_queues[self.id].get(timeout=1)
                self.airport.monitor.increment_usage("gates", self.id)
                
                self.process_passenger(passenger)
                
                self.airport.gates_queues[self.id].task_done()
                self.airport.monitor.decrement_usage("gates", self.id)
                
            except Empty:
                pass
            
    def process_passenger(self, passenger):
        print(f"{passenger.name} is boarding at gate {self.id}. Flight: {passenger.flight_nb}")
        time_ = random.randint(1, 5)
        time.sleep(time_)