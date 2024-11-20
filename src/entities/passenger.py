# entities/passenger.py
import random

class Passenger:
    passenger_id_counter = 1

    def __init__(self, name, type, origin, nb_suitcases, nb_bags, terminal, airline, flight_nb, destination, airport, gate_id):
        self.id = Passenger.passenger_id_counter
        Passenger.passenger_id_counter += 1
        self.name = name
        self.type = type
        self.origin = origin
        self.nb_suitcases = nb_suitcases
        self.nb_bags = nb_bags
        self.terminal = terminal
        self.airline = airline
        self.flight_nb = flight_nb
        self.destination = destination
        self.airport = airport
        self.gate_id = gate_id

    @staticmethod
    def generate_random_passenger(airport, passenger_type):
        names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
        terminals = ["T1", "T2", "T3"]
        flight = random.choice(airport.available_flights)
        gate_id = airport.flights_to_gates[flight]

        return Passenger(
            name=random.choice(names),
            type=passenger_type,
            origin="Home" if passenger_type == "departing" else "Madrid Airport",
            nb_suitcases=random.randint(1, 3),
            nb_bags=random.randint(1, 2),
            terminal=random.choice(terminals),
            airline=flight.split()[0],
            flight_nb=flight,
            destination="City Center" if passenger_type == "arriving" else "Madrid Airport",
            airport=airport,
            gate_id=gate_id
        )