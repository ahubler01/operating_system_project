# entities/passenger.py
import random

class Passenger:
    passenger_id_counter = 1
    used_names = set()

    def __init__(
        self, 
        name, type, origin, 
        p_luggage, nb_suitcases, nb_bags, 
        p_shop, money, airline, 
        flight_nb, destination, airport, 
        gate_id
        ):
        
        self.id = Passenger.passenger_id_counter
        Passenger.passenger_id_counter += 1

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
        names = [
            "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hannah", "Isaac", "Jack",
            "Katie", "Liam", "Mia", "Nathan", "Olivia", "Paul", "Quinn", "Rachel", "Samuel", "Tina",
            "Uma", "Victor", "Wendy", "Xavier", "Yvonne", "Zach", "Adrian", "Bella", "Caleb", "Delilah",
            "Ethan", "Fiona", "Gavin", "Hailey", "Ian", "Julia", "Kyle", "Luna", "Mason", "Nina"
        ]
        available_names = [name for name in names if name not in Passenger.used_names]
        
        if not available_names:
            raise ValueError("All names have been used. Add more names to the list.")
        
        chosen_name = random.choice(available_names)
        Passenger.used_names.add(chosen_name) 
        
        flight = random.choice(airport.available_flights)
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
            airline=flight.split()[0],
            flight_nb=flight,
            destination="City Center" if passenger_type == "arriving" else "Madrid Airport",
            airport=airport,
            gate_id=gate_id
        )