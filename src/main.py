# main.py

import threading
import time
from queue import Queue
from entities.taxi import Taxi
from entities.passenger import Passenger
import random

def generate_departing_passengers(queue):
    passenger_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    airlines = ['Iberia', 'Air Europa', 'Ryanair', 'Vueling', 'EasyJet']
    flights = ['IB123', 'AE456', 'FR789', 'VY101', 'U222']
    terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4', 'Terminal 4S']

    for i in range(len(passenger_names)):
        name = passenger_names[i]
        type = 'departing'
        origin = 'Home Address'
        terminal = random.choice(terminals)
        airline = random.choice(airlines)
        flight_nb = random.choice(flights)
        destination = 'Madrid Airport'

        passenger = Passenger(name, type, origin, terminal, airline, flight_nb, destination)
        print(f"{passenger.name} ({type}) needs to go to {destination}, Terminal: {terminal}, Flight: {flight_nb}")
        queue.put(passenger)
        time.sleep(1)  # Simulate time between passenger requests

def generate_arriving_passengers(queue):
    passenger_names = ['Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
    airlines = ['Iberia', 'Air Europa', 'Ryanair', 'Vueling', 'EasyJet']
    flights = ['IB321', 'AE654', 'FR987', 'VY202', 'U333']
    terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4', 'Terminal 4S']
    destinations = ['Sol', 'Chueca', 'Lavapiés', 'Malasaña', 'Retiro']

    for i in range(len(passenger_names)):
        name = passenger_names[i]
        type = 'arriving'
        origin = 'Madrid Airport'
        terminal = random.choice(terminals)
        airline = random.choice(airlines)
        flight_nb = random.choice(flights)
        destination = random.choice(destinations)

        passenger = Passenger(name, type, origin, terminal, airline, flight_nb, destination)
        print(f"{passenger.name} ({type}) needs to go to {destination} from {origin}, Terminal: {terminal}, Flight: {flight_nb}")
        queue.put(passenger)
        time.sleep(1)  # Simulate time between passenger arrivals

if __name__ == "__main__":
    city_to_airport_queue = Queue()
    airport_to_city_queue = Queue()

    # Start passenger generators
    threading.Thread(target=generate_departing_passengers, args=(city_to_airport_queue,)).start()
    threading.Thread(target=generate_arriving_passengers, args=(airport_to_city_queue,)).start()

    # Create taxis
    taxis = [Taxi(city_to_airport_queue, airport_to_city_queue) for _ in range(3)]

    # Start taxi threads
    for taxi in taxis:
        taxi.start()

    # Wait for all passengers to be processed
    city_to_airport_queue.join()
    airport_to_city_queue.join()

    # Wait for all taxis to finish
    for taxi in taxis:
        taxi.join()

    print("Simulation finished.")
