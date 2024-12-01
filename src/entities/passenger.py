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

        with airport.flight_capacity_lock:
            # Find flights with available capacity and assigned gates
            available_flights = [
                flight for flight, capacity in airport.flight_capacities.items()
                if capacity > 0 and flight in airport.flights_to_gates
            ]

            if not available_flights:
                return None  # No flights with available capacity and assigned gates

            chosen_name = Passenger.passenger_id_counter
            Passenger.passenger_id_counter += 1

            # Select a random flight that has capacity and a gate assigned
            flight = random.choice(available_flights)
            gate_id = airport.flights_to_gates[flight]

            # Decrement the capacity
            airport.flight_capacities[flight] -= 1

        return Passenger(
            name=chosen_name,
            type=passenger_type,
            origin="Home" if passenger_type == "departing" else "Madrid Airport",
            nb_suitcases=random.randint(1, 3),
            nb_bags=random.randint(1, 2),
            p_luggage=random.random(),
            p_shop=random.random(),
            money=random.randint(50, 200),
            airline=flight[:2], 
            flight_nb=flight,
            destination="City Center" if passenger_type == "arriving" else "Madrid Airport",
            airport=airport,
            gate_id=gate_id
        )