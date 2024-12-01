# entities/aircraft.py

import threading
import time
import random

# Add this import statement
from entities.passenger import Passenger

class Aircraft(threading.Thread):
    def __init__(self, flight_number, gate_id, departure_time, airport):
        super().__init__()
        self.flight_number = flight_number
        self.gate_id = gate_id
        self.departure_time = departure_time
        self.airport = airport
        self.max_capacity = 30  # Maximum number of passengers
        self.boarded_passengers = 0  # Current number of boarded passengers
        self.boarding_complete = threading.Event()  # Event to signal boarding complete
        self.lock = threading.Lock()  # Lock to protect boarded_passengers

    def assign_gate(self, gate_id):
        self.gate_id = gate_id

    def generate_arriving_passengers(self):
        """Generate arriving passengers from this aircraft."""
        num_arriving_passengers = random.randint(10, 30)
        for _ in range(num_arriving_passengers):
            passenger = Passenger.generate_random_passenger(self.airport, "arriving")
            if passenger:
                with self.airport.passenger_count_lock:
                    self.airport.total_passengers += 1
                self.airport.airport_to_city_queue.put(passenger)

    def passenger_boarded(self):
        """Increment boarded passengers count and check if boarding is complete."""
        with self.lock:
            self.boarded_passengers += 1
            if self.boarded_passengers >= self.max_capacity:
                # Boarding is complete
                self.boarding_complete.set()

    def run(self):
        while not self.airport.simulation_end.is_set():
            if self.gate_id is None:
                return  # Cannot run without a gate

            # Register the aircraft as active
            self.airport.register_active_aircraft(self)

            print(f"Aircraft {self.flight_number} has arrived at Gate {self.gate_id}.")

            # Generate arriving passengers
            self.generate_arriving_passengers()

            # Wait until boarding is complete or timeout occurs
            boarding_timeout = 300  # 5 minutes in seconds
            boarding_complete = self.boarding_complete.wait(timeout=boarding_timeout)

            if boarding_complete:
                print(f"Flight {self.flight_number} has completed boarding with {self.boarded_passengers} passengers.")
            else:
                print(f"Flight {self.flight_number} is departing after timeout with {self.boarded_passengers} passengers.")

            print(f"Flight {self.flight_number} is departing from Gate {self.gate_id}.")

            # Release the gate after departure
            self.airport.release_gate(self.gate_id, self.flight_number)

            # Deregister the aircraft after departure
            self.airport.deregister_active_aircraft(self)
