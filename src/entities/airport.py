# entities/airport.py
import threading
import time
import random
from queue import Queue
from entities.taxi import Taxi
from entities.passenger import Passenger
from entities.counter import Counter
from entities.security import Security
from entities.shops import Shops
from entities.gates import Gates

class Airport:
    def __init__(self, num_counters, num_taxis, num_security_lines, num_passengers, num_shops, num_gates, num_flights):
        self.city_to_airport_queue = Queue()
        self.airport_to_city_queue = Queue()
        self.counter_queue = Queue()
        self.security_check_queue = Queue()
        self.shops_queues = [Queue() for _ in range(num_shops)]
        self.gates_queues = [Queue() for _ in range(num_gates)]

        self.simulation_end = threading.Event()

        self.counters = [Counter(i, self) for i in range(num_counters)]
        self.security_lines = [Security(i, self) for i in range(num_security_lines)]
        self.taxis = [
            Taxi(self.city_to_airport_queue, self.airport_to_city_queue, self)
            for _ in range(num_taxis)
        ]
        self.shops = [Shops(i, self) for i in range(num_shops)]
        self.gates = [Gates(i, self) for i in range(num_gates)]

        # Set available flights and map them to gates
        all_flights = ["IB123", "FR456", "VY789", "EJ101", "BA202", "LH303"]
        self.available_flights = random.sample(all_flights, num_flights)
        self.flights_to_gates = {self.available_flights[i]: i % num_gates for i in range(num_flights)}

        # Generate passengers
        for _ in range(num_passengers // 2):
            passenger = Passenger.generate_random_passenger(self, "departing")
            self.city_to_airport_queue.put(passenger)

        for _ in range(num_passengers // 2):
            passenger = Passenger.generate_random_passenger(self, "arriving")
            self.airport_to_city_queue.put(passenger)

    def start_simulation(self):
        # Start counters and security lines
        for counter in self.counters:
            counter.start()

        for security in self.security_lines:
            security.start()
            
        for shop in self.shops:
            shop.start()
        
        for gate in self.gates:
            gate.start()

        # Start taxis
        for taxi in self.taxis:
            taxi.start()

        # Wait for queues to empty
        self.city_to_airport_queue.join()
        self.airport_to_city_queue.join()
        self.counter_queue.join()
        self.security_check_queue.join()
        for shop_queue in self.shops_queues:
            shop_queue.join()
        for gate_queue in self.gates_queues:
            gate_queue.join()

        # Signal simulation end
        self.simulation_end.set()

        # Join all threads
        for counter in self.counters:
            counter.is_active = False
            counter.join()
        
        for security in self.security_lines:
            security.join()
            
        for shop in self.shops:
            shop.is_active = False
            shop.join()
            
        for gate in self.gates:
            gate.is_active = False
            gate.join()
            
        for taxi in self.taxis:
            taxi.is_active = False
            taxi.join()