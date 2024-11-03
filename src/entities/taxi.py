# entities/taxi.py

import threading
import time
from queue import Queue, Empty

class Taxi(threading.Thread):
    taxi_id_counter = 1
    taxi_id_lock = threading.Lock()

    def __init__(self, city_to_airport_queue, airport_to_city_queue):
        super().__init__()
        with Taxi.taxi_id_lock:
            self.id = Taxi.taxi_id_counter
            Taxi.taxi_id_counter += 1
        self.city_to_airport_queue = city_to_airport_queue
        self.airport_to_city_queue = airport_to_city_queue

    def run(self):
        # First, pick up departing passengers (from city to airport)
        try:
            passenger = self.city_to_airport_queue.get(timeout=5)
            print(f"Taxi {self.id} picked up {passenger.name} ({passenger.type}) from {passenger.origin} to {passenger.destination}.")
            print(f"Passenger details: Terminal {passenger.terminal}, Airline {passenger.airline}, Flight {passenger.flight_nb}")
            # Simulate driving to the airport
            time.sleep(2)
            print(f"Passenger {passenger.id} ({passenger.name}) arrives at {passenger.destination} with Taxi {self.id}.")
            self.city_to_airport_queue.task_done()
        except Empty:
            # No passengers to pick up to the airport
            print(f"Taxi {self.id} found no departing passengers.")
            pass

        # Taxi becomes available at the airport
        print(f"Taxi {self.id} is now available at the airport.")

        # Then, pick up arriving passengers (from airport to city)
        try:
            passenger = self.airport_to_city_queue.get(timeout=5)
            print(f"Taxi {self.id} picked up {passenger.name} ({passenger.type}) from {passenger.origin} to {passenger.destination}.")
            print(f"Passenger details: Terminal {passenger.terminal}, Airline {passenger.airline}, Flight {passenger.flight_nb}")
            # Simulate driving to the destination
            time.sleep(2)
            print(f"Taxi {self.id} dropped off Passenger {passenger.id} ({passenger.name}) at {passenger.destination}.")
            self.airport_to_city_queue.task_done()
        except Empty:
            # No passengers to pick up from the airport
            print(f"Taxi {self.id} found no arriving passengers.")
            pass

        print(f"Taxi {self.id} has completed its trips.")
