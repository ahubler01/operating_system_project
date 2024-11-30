# entities/taxi.py
import threading
import time
from queue import Empty
import random 


class Taxi(threading.Thread):
    taxi_id_counter = 1
    taxi_id_lock = threading.Lock()

    def __init__(self, 
                 city_to_airport_queue, 
                 airport_to_city_queue, 
                 airport
                ):
        
        super().__init__()
        with Taxi.taxi_id_lock:
            self.id = Taxi.taxi_id_counter
            Taxi.taxi_id_counter += 1
        self.city_to_airport_queue = city_to_airport_queue
        self.airport_to_city_queue = airport_to_city_queue
        self.is_active = True
        self.airport = airport

    def run(self):
        while self.is_active:
            self.pick_up(self.city_to_airport_queue, "city_to_airport")
            self.pick_up(self.airport_to_city_queue, "airport_to_city")

    def pick_up(self, queue, direction):
        try:
            passenger = queue.get(timeout=5)
            print(f"Taxi {self.id} picked up {passenger.name} for {direction}.")
            self.airport.monitor.increment_usage(f"taxis_{direction}", self.id)
            self.simulate_drive(passenger, direction)
            queue.task_done()
            self.airport.monitor.decrement_usage(f"taxis_{direction}", self.id)
            if direction == "city_to_airport":
                self.airport.counter_queue.put(passenger)
            elif direction == "airport_to_city":
                pass
        except Empty:
            pass

    def simulate_drive(self, passenger, direction):
        time_ = random.randint(1, 10)
        time.sleep(time_)
        print(f"Taxi {self.id} dropped off {passenger.name} at destination.")
        if direction == "airport_to_city":
            with self.airport.passenger_count_lock:
                self.airport.total_passengers -= 1

    def stop(self):
        """Stop the taxi thread."""
        self.is_active = False
        self.join()