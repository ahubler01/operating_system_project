# entities/gates.py

import threading
import time
import random
from queue import Empty

class Gates(threading.Thread):
    def __init__(self, id, airport):
        super().__init__()
        self.id = id
        self.airport = airport
        self.is_active = True
        self.current_aircraft = None
        self.aircraft_assigned_event = threading.Event()

    def run(self):
        while self.is_active and not self.airport.simulation_end.is_set():
            if self.current_aircraft is None:
                # Wait until an aircraft is assigned
                self.aircraft_assigned_event.wait(timeout=1)
                continue  # Check again for aircraft assignment
            else:
                try:
                    passenger = self.airport.gates_queues[self.id].get(timeout=1)
                    self.airport.monitor.increment_usage("gates", self.id)
                    
                    self.process_passenger(passenger)
                    
                    self.airport.gates_queues[self.id].task_done()
                    self.airport.monitor.decrement_usage("gates", self.id)
                except Empty:
                    pass

    def assign_aircraft(self, aircraft):
        self.current_aircraft = aircraft
        self.aircraft_assigned_event.set()
        print(f"Gate {self.id} assigned to Aircraft {aircraft.flight_number}.")

    def release_aircraft(self):
        if self.current_aircraft:
            print(f"Gate {self.id} released from Aircraft {self.current_aircraft.flight_number}.")
        else:
            print(f"Gate {self.id} had no aircraft to release.")
        self.current_aircraft = None
        self.aircraft_assigned_event.clear()

    def process_passenger(self, passenger):
        print(f"{passenger.name} is boarding at gate {self.id}. Flight: {passenger.flight_nb}")
        time_ = random.randint(1, 5)
        time.sleep(time_)
        # Decrement the total passengers count after boarding
        with self.airport.passenger_count_lock:
            self.airport.total_passengers -= 1
        # Notify the aircraft that a passenger has boarded
        if self.current_aircraft:
            self.current_aircraft.passenger_boarded()
        else:
            print(f"No aircraft assigned to gate {self.id}")

    def stop(self):
        """Stop the gate thread."""
        self.is_active = False
        self.join()
