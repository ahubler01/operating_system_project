# entities/passenger.py
import random
import threading

class Passenger:
    passenger_id_counter = 1

    def __init__(
        self, 
        name, type, origin, 
        p_luggage, nb_suitcases, nb_bags, 
        p_shop, money, airline, 
        flight_nb, destination, airport, 
        gate_id
    ):
        self.id = name
        self.name = name
        self.type = type
        self.origin = origin
        self.p_luggage = p_luggage
        self.nb_suitcases = nb_suitcases
        self.nb_bags = nb_bags
        self.p_shop = p_shop
        self.money = money
        self.airline = airline
        self.flight_nb = flight_nb
        self.destination = destination
        self.airport = airport
        self.gate_id = gate_id

    @staticmethod
    def generate_random_passenger(airport, passenger_type):
        # Ensure there are flights with assigned gates
        if not airport.flights_to_gates:
            return None  # No flights available yet

        chosen_name = Passenger.passenger_id_counter
        Passenger.passenger_id_counter += 1

        # Select a random flight that has a gate
        flight = random.choice(list(airport.flights_to_gates.keys()))
        gate_id = airport.flights_to_gates[flight]

        return Passenger(
            name=chosen_name,
            type=passenger_type,
            origin="Home" if passenger_type == "departing" else "Madrid Airport",
            nb_suitcases=random.randint(1, 3),
            nb_bags=random.randint(1, 2),
            p_luggage=random.random(),
            p_shop=random.random(),
            money=random.randint(50, 200),
            airline=flight[:2],  # Assuming airline code is the first two letters
            flight_nb=flight,
            destination="City Center" if passenger_type == "arriving" else "Madrid Airport",
            airport=airport,
            gate_id=gate_id
        )