# entities/taxi.py
import threading
import time
from queue import Empty


class Taxi(threading.Thread):
    taxi_id_counter = 1
    taxi_id_lock = threading.Lock()

    def __init__(self, city_to_airport_queue, airport_to_city_queue, airport):
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
            self.simulate_drive(passenger)
            queue.task_done()
            if direction == "city_to_airport":
                self.airport.counter_queue.put(passenger)
            elif direction == "airport_to_city":
                pass
        except Empty:
            pass

    def simulate_drive(self, passenger):
        time.sleep(2)
        print(f"Taxi {self.id} dropped off {passenger.name} at destination.")
