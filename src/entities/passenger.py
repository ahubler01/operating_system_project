class Passenger:
    passenger_id_counter = 1

    def __init__(self, name, type, origin, terminal, airline, flight_nb, destination):
        self.id = Passenger.passenger_id_counter
        Passenger.passenger_id_counter += 1
        self.name = name,
        self.type = type,
        self.origin = origin,
        self.terminal = terminal,
        self.airline = airline,
        self.flight_nb = flight_nb,
        self.destination = destination

    def __str__(self):
        return (f"Passenger {self.id}: {self.name} {self.type} from {self.origin} to {self.destination}, "
                f"Terminal: {self.terminal}, Airline: {self.airline}, Flight Number: {self.flight_nb}")