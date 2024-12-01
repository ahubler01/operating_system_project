# entities/airport.py

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
    def __init__(self, 
                 num_counters, 
                 num_taxis, 
                 num_security_lines, 
                 num_passengers, 
                 num_shops, 
                 num_gates, 
                 num_flights, 
                 dynamic_scaling_enabled=False, 
                 export_timeseries_data=False
                ):
        
        # Initialize queues
        self.city_to_airport_queue = Queue()
        self.airport_to_city_queue = Queue()
        self.counter_queue = Queue()
        self.security_check_queue = Queue()
        self.shops_queues = [Queue() for _ in range(num_shops)]
        self.gates_queues = {} 

        self.simulation_end = threading.Event()  # Will only be set when the simulation is to end

        # Initialize entities
        self.counters = [Counter(i, self) for i in range(num_counters)]
        self.security_lines = [Security(i, self) for i in range(num_security_lines)]
        self.shops = [Shops(i, self) for i in range(num_shops)]
        
        # Initialize gates and their queues
        self.gates = [Gates(gate_id, self) for gate_id in range(num_gates)]
        self.gates_queues = {gate_id: Queue() for gate_id in range(num_gates)}

        # Start gate entities
        for gate in self.gates:
            gate.start()

        self.taxis = [Taxi(self.city_to_airport_queue, self.airport_to_city_queue, self) for _ in range(num_taxis)]

        self.monitor = Monitor(self, export_timeseries_data)
        self.gui_monitor = GUIMonitor(self.monitor)

        # Initialize flights and aircraft
        self.aircrafts = []
        self.all_flights = [] 
        self.flights_to_gates = {}  
        self.flights_to_aircraft = {}  
        self.gate_to_aircraft = {}     
        self.gate_availability = set(range(num_gates))  #
        self.aircraft_queue = Queue()

        self.passengers_per_gate = {}

        self.flight_capacities = {}
        self.flight_capacity_lock = threading.Lock()

        self.total_passengers = 0
        self.passenger_count_lock = threading.Lock()

        # Active aircrafts
        self.active_aircrafts = []
        self.aircraft_lock = threading.Lock()
        self.dynamic_scaling_enabled = dynamic_scaling_enabled 

        self.init_flights(num_flights)

        # Generate passengers after flights and gates are initialized
        self.generate_initial_passengers(num_passengers)

        # Start monitoring usage stats
        self.monitor.start_monitoring()

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
                    self.flights_to_gates[aircraft.flight_number] = gate_id  
                    self.flights_to_aircraft[aircraft.flight_number] = aircraft 
                    self.gate_to_aircraft[gate_id] = aircraft
                    self.passengers_per_gate[gate_id] = 0  

                    # Assign aircraft to the existing gate entity
                    gate_entity = self.gates[gate_id]
                    gate_entity.assign_aircraft(aircraft)

                    print(f"Gate {gate_id} allocated to Aircraft {aircraft.flight_number}.")
                    aircraft.start()
                    self.aircrafts.append(aircraft)
                else:
                    # No gates available, put the aircraft back in the queue
                    self.aircraft_queue.put(aircraft)
                    time.sleep(1)  # Wait a bit before retrying
            except Empty:
                continue

    def register_active_aircraft(self, aircraft):
        with self.aircraft_lock:
            self.active_aircrafts.append(aircraft)

    def deregister_active_aircraft(self, aircraft):
        with self.aircraft_lock:
            if aircraft in self.active_aircrafts:
                self.active_aircrafts.remove(aircraft)

    def add_new_aircraft(self):
        """Add new aircraft to the queue with flight numbers."""
        flight_index = 0

        # Add the first aircraft immediately
        flight_number = self.all_flights[flight_index % len(self.all_flights)]
        flight_index += 1
        aircraft = Aircraft(flight_number, None, None, self)
        with self.flight_capacity_lock:
            self.flight_capacities[flight_number] = aircraft.max_capacity
        self.aircraft_queue.put(aircraft)
        print(f"Aircraft {flight_number} added to the queue immediately.")

        while not self.simulation_end.is_set():
            time.sleep(random.randint(10, 30))  # Wait before adding a new aircraft
            if self.simulation_end.is_set():
                break  # Exit if simulation has ended
            flight_number = self.all_flights[flight_index % len(self.all_flights)]
            flight_index += 1
            aircraft = Aircraft(flight_number, None, None, self)
            with self.flight_capacity_lock:
                self.flight_capacities[flight_number] = aircraft.max_capacity
            self.aircraft_queue.put(aircraft)
            print(f"Aircraft {flight_number} added to the queue.")

    def release_gate(self, gate_id, flight_number):
        """Release a gate after a flight departs."""
        self.gate_availability.add(gate_id)

        del self.flights_to_gates[flight_number]  
        del self.flights_to_aircraft[flight_number] 
        del self.gate_to_aircraft[gate_id]

        with self.flight_capacity_lock:
            del self.flight_capacities[flight_number]
        
        # Reset passenger count for the gate
        self.passengers_per_gate[gate_id] = 0

        # Release the aircraft from the gate entity
        gate_entity = self.gates[gate_id]
        gate_entity.release_aircraft()

        print(f"Gate {gate_id} is now available.")

    def generate_initial_passengers(self, num_passengers):
        """Generate initial departing passengers after flights are set up."""
        # Wait until at least one flight has a gate assigned
        while not self.flights_to_gates:
            time.sleep(1)

        print(f"Generating {num_passengers} initial departing passengers.")

        # Generate only departing passengers
        for _ in range(num_passengers):
            passenger = Passenger.generate_random_passenger(self, "departing")
            if passenger:
                self.city_to_airport_queue.put(passenger)
                print(f"Passenger {passenger.name} added to city_to_airport_queue.")

    def generate_passengers(self):
        """Continuously generate departing passengers during simulation."""
        while not self.simulation_end.is_set():
            time_ = random.randint(1, 5)
            time.sleep(time_)
            if self.simulation_end.is_set():
                break  # Exit if simulation has ended
            passenger = Passenger.generate_random_passenger(self, "departing")
            if passenger:
                self.city_to_airport_queue.put(passenger)

    def add_entity(self, station_type):
        """Add a new entity of the specified type."""
        time.sleep(1)  
        if station_type == "counters":
            new_id = len(self.counters)
            counter = Counter(new_id, self)
            self.counters.append(counter)
            self.monitor.total_entities["counters"] += 1
            counter.start()
            print(f"Added new counter {new_id}")
        elif station_type == "security":
            new_id = len(self.security_lines)
            security = Security(new_id, self)
            self.security_lines.append(security)
            self.monitor.total_entities["security"] += 1
            security.start()
            print(f"Added new security line {new_id}")
        elif station_type == "shops":
            new_id = len(self.shops)
            shop = Shops(new_id, self)
            self.shops.append(shop)
            self.shops_queues.append(Queue()) 
            self.monitor.total_entities["shops"] += 1
            shop.start()
            print(f"Added new shop {new_id}")
        elif station_type == "taxis":
            taxi = Taxi(self.city_to_airport_queue, self.airport_to_city_queue, self)
            self.taxis.append(taxi)
            self.monitor.total_entities["taxis"] += 1
            taxi.start()
            print(f"Added new taxi {taxi.id}")
        else:
            print(f"Unknown station type: {station_type}")

    def remove_entity(self, station_type):
        """Remove an entity of the specified type, if possible."""
        time.sleep(1)  

        if station_type == "counters":
            with threading.Lock():
                if len(self.counters) > 1:
                    entity_to_remove = self.counters.pop()
                    entity_to_remove.stop()
                    self.monitor.total_entities["counters"] -= 1
                    print(f"Removed counter {entity_to_remove.id}")
                else:
                    print("Cannot remove counter: minimum number reached.")

        elif station_type == "security":
            with threading.Lock():
                if len(self.security_lines) > 1:
                    entity_to_remove = self.security_lines.pop()
                    entity_to_remove.stop()
                    self.monitor.total_entities["security"] -= 1
                    print(f"Removed security line {entity_to_remove.id}")
                else:
                    print("Cannot remove security line: minimum number reached.")

        elif station_type == "shops":
            with threading.Lock():
                if len(self.shops) > 1:
                    entity_to_remove = self.shops.pop()
                    entity_to_remove.stop()
                    self.shops_queues.pop()
                    self.monitor.total_entities["shops"] -= 1
                    print(f"Removed shop {entity_to_remove.id}")
                else:
                    print("Cannot remove shop: minimum number reached.")

        elif station_type == "taxis":
            with threading.Lock():
                if len(self.taxis) > 1:
                    entity_to_remove = self.taxis.pop()
                    entity_to_remove.stop()
                    self.monitor.total_entities["taxis"] -= 1
                    print(f"Removed taxi {entity_to_remove.id}")
                else:
                    print("Cannot remove taxi: minimum number reached.")

        else:
            print(f"Unknown station type: {station_type}")
            
    def start_simulation(self):
        """Start the airport simulation."""
        # Start entity threads
        for entity in self.counters + self.security_lines + self.shops + self.taxis:
            entity.start()

        # Start passenger and taxi generation threads
        threading.Thread(target=self.generate_passengers, daemon=True).start()

        start_time = time.time()
        try:
            while not self.simulation_end.is_set():
                time.sleep(1)
                elapsed_time = time.time() - start_time
                if elapsed_time >= 2:
                    print("Simulation time of 1 minute has elapsed. Stopping simulation.")
                    self.stop_simulation()
        except KeyboardInterrupt:
            self.stop_simulation()  

    def stop_simulation(self):
        """Stop the simulation and clean up."""
        self.simulation_end.set()

        # Stop all entities
        for entity in self.counters + self.security_lines + self.shops + self.gates + self.taxis:
            entity.is_active = False

        # Similarly for aircraft threads
        for aircraft in self.aircrafts:
            aircraft.is_active = False

        # Stop monitoring
        self.monitor.stop_monitoring()

        # Stop GUI monitor
        self.gui_monitor.stop()

