import threading
import time
import random
from queue import Queue, Empty
from entities.taxi import Taxi
from entities.passenger import Passenger
from entities.counter import Counter
from entities.security import Security
from entities.shops import Shops
from entities.gates import Gates
from entities.aircraft import Aircraft

from gui_monitor import GUIMonitor
from monitor import Monitor

class Airport:
    def __init__(self, num_counters, num_taxis, num_security_lines, num_passengers, num_shops, num_gates, num_flights):
        # Initialize queues
        self.city_to_airport_queue = Queue()
        self.airport_to_city_queue = Queue()
        self.counter_queue = Queue()
        self.security_check_queue = Queue()
        self.shops_queues = [Queue() for _ in range(num_shops)]
        self.gates_queues = [Queue() for _ in range(num_gates)]

        self.simulation_end = threading.Event()  # Will only be set when the simulation is to end

        # Initialize entities
        self.counters = [Counter(i, self) for i in range(num_counters)]
        self.security_lines = [Security(i, self) for i in range(num_security_lines)]
        self.shops = [Shops(i, self) for i in range(num_shops)]
        self.gates = [Gates(i, self) for i in range(num_gates)]
        self.taxis = [Taxi(self.city_to_airport_queue, self.airport_to_city_queue, self) for _ in range(num_taxis)]

        self.monitor = Monitor(self)
        self.gui_monitor = GUIMonitor(self.monitor)

        # Initialize flights and aircraft
        self.aircrafts = []
        self.flights_to_gates = {}  # Map flights to gates
        self.gate_availability = set(range(num_gates))  # Gates available
        self.aircraft_queue = Queue()  # Aircraft waiting for gates

        self.init_flights(num_flights)

        # Generate passengers after flights and gates are initialized
        self.generate_initial_passengers(num_passengers)

    def init_flights(self, num_flights):
        """Initialize flights and aircraft before generating passengers."""
        prefixes = ["IB", "FR", "VY", "EJ", "BA", "LH"]
        self.all_flights = [f"{random.choice(prefixes)}{random.randint(100, 999)}" for _ in range(num_flights)]

        # Start aircraft threads and manage gate assignments
        threading.Thread(target=self.manage_gates, daemon=True).start()
        threading.Thread(target=self.add_new_aircraft, daemon=True).start()

    def manage_gates(self):
        """Manage gate allocation for aircraft."""
        while not self.simulation_end.is_set():
            try:
                aircraft = self.aircraft_queue.get(timeout=5)
                if self.gate_availability:
                    gate_id = self.gate_availability.pop()
                    aircraft.assign_gate(gate_id)
                    self.flights_to_gates[aircraft.flight_number] = gate_id  # Map flight to gate
                    print(f"Gate {gate_id} allocated to Aircraft {aircraft.flight_number}.")
                    aircraft.start()
                    self.aircrafts.append(aircraft)
                else:
                    # No gates available, put the aircraft back in the queue
                    self.aircraft_queue.put(aircraft)
            except Empty:
                continue

    def add_new_aircraft(self):
        """Add new aircraft to the queue with flight numbers."""
        flight_index = 0
        while not self.simulation_end.is_set():
            time.sleep(random.randint(10, 30))  # Wait before adding a new aircraft
            flight_number = self.all_flights[flight_index % len(self.all_flights)]
            flight_index += 1
            aircraft = Aircraft(flight_number, None, None, self)
            self.aircraft_queue.put(aircraft)
            print(f"Aircraft {flight_number} added to the queue.")

    def release_gate(self, gate_id, flight_number):
        """Release a gate after a flight departs."""
        self.gate_availability.add(gate_id)
        del self.flights_to_gates[flight_number]  # Remove the flight-to-gate mapping
        print(f"Gate {gate_id} is now available.")

    def generate_initial_passengers(self, num_passengers):
        """Generate initial passengers after flights are set up."""
        # Wait until at least one flight has a gate assigned
        while not self.flights_to_gates:
            time.sleep(1)

        # Generate departing passengers
        for _ in range(num_passengers // 2):
            passenger = Passenger.generate_random_passenger(self, "departing")
            if passenger:
                self.city_to_airport_queue.put(passenger)

        # Generate arriving passengers
        for _ in range(num_passengers // 2):
            passenger = Passenger.generate_random_passenger(self, "arriving")
            if passenger:
                self.airport_to_city_queue.put(passenger)

    def generate_passengers(self):
        """Continuously generate passengers during simulation."""
        while not self.simulation_end.is_set():
            time.sleep(2)  # Generate new passengers every 15 seconds
            passenger_type = random.choice(["departing", "arriving"])
            passenger = Passenger.generate_random_passenger(self, passenger_type)
            if passenger:
                if passenger_type == "departing":
                    self.city_to_airport_queue.put(passenger)
                else:
                    self.airport_to_city_queue.put(passenger)

    def add_taxis_periodically(self):
        """Add taxis to the simulation periodically."""
        while not self.simulation_end.is_set():
            time.sleep(30)
            taxi = Taxi(self.city_to_airport_queue, self.airport_to_city_queue, self)
            self.taxis.append(taxi)
            taxi.start()

    def start_simulation(self):
        """Start the airport simulation."""
        # Start entity threads
        for entity in self.counters + self.security_lines + self.shops + self.gates + self.taxis:
            entity.start()

        # Start passenger and taxi generation threads
        threading.Thread(target=self.generate_passengers, daemon=True).start()
        threading.Thread(target=self.add_taxis_periodically, daemon=True).start()

        # Simulation runs indefinitely until manually terminated
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_simulation()

    def stop_simulation(self):
        """Stop the simulation and clean up."""
        self.simulation_end.set()

        # Stop all entities
        for entity in self.counters + self.security_lines + self.shops + self.gates + self.taxis:
            entity.is_active = False

        # Wait for all entities to finish
        for entity in self.counters + self.security_lines + self.shops + self.gates + self.taxis:
            entity.join()

        # Wait for aircraft threads to finish
        for aircraft in self.aircrafts:
            aircraft.join()

        # Stop monitoring
        self.monitor.stop_monitoring()