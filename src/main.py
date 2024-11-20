# main.py
import threading
import time
from queue import Queue
from entities.taxi import Taxi
from entities.passenger import Passenger
from entities.counter import Counter
from entities.airport import Airport
import random

if __name__ == "__main__":
    num_counters = 3
    num_security_lines = 2
    num_taxis = 6
    num_passengers = 10
    num_shops = 5
    num_gates = 3
    num_flights = 3
    
    airport = Airport(
        num_counters=num_counters, num_taxis=num_taxis, 
        num_security_lines=num_security_lines, num_passengers=num_passengers,
        num_shops=num_shops, num_gates=num_gates,
        num_flights=num_flights
    )

    airport.start_simulation()

    print("Simulation finished.")