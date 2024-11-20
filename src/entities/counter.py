# entities/counter.py
import threading
from queue import Empty
import time 

class Counter(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True

    def run(self):
        while self.is_active:
            try:
                passenger = self.airport.counter_queue.get(timeout=1)
                print(f"Counter {self.id} serving {passenger.name}.")
                time.sleep(2)
                self.airport.security_check_queue.put(passenger)
            except Empty:
                pass

    def process_passenger(self, passenger):
        print(f"Counter {self.id} processing {passenger.name}.")
        time.sleep(2)
