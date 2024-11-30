# entities/aircraft.py
import threading
import time
from queue import Empty
import random

class Aircraft(threading.Thread):
    def __init__(self, 
                 flight_number, 
                 gate_id, 
                 departure_time, 
                 airport
                ):
        
        super().__init__()
        self.flight_number = flight_number
        self.gate_id = gate_id
        self.departure_time = departure_time
        self.airport = airport

    def assign_gate(self, gate_id):
        """Assign a gate to the aircraft and set the departure time."""
        self.gate_id = gate_id
        self.departure_time = time.time() + random.randint(30, 120)  # Departure in 30-120 seconds

    def run(self):
        if self.gate_id is None:
            return  # Cannot run without a gate

        self.airport.register_active_aircraft(self)
            
        print(f"Aircraft {self.flight_number} has arrived at Gate {self.gate_id}.")
        print(f"Scheduled departure time: {time.strftime('%H:%M:%S', time.localtime(self.departure_time))}")

        boarding_start_time = self.departure_time - 5
        while time.time() < boarding_start_time and not self.airport.simulation_end.is_set():
            time.sleep(1)

        if self.airport.simulation_end.is_set():
            return

        print(f"Boarding for flight {self.flight_number} at Gate {self.gate_id} has started.")

        # Simulate boarding
        time.sleep(3)  

        print(f"Flight {self.flight_number} is departing from Gate {self.gate_id}.")

        self.airport.release_gate(self.gate_id, self.flight_number)
        self.airport.deregister_active_aircraft(self)