# entities/aircraft.py
import threading
import time
from queue import Empty

class Aircraft(threading.Thread):
    def __init__(self, flight_number, gate_id, departure_time, airport):
        super().__init__()
        self.flight_number = flight_number
        self.gate_id = gate_id
        self.departure_time = departure_time  # Seconds since simulation start
        self.airport = airport

    def run(self):
        # Print aircraft arrival details
        print(f"Aircraft {self.flight_number} has arrived at Gate {self.gate_id}.")
        print(f"Scheduled departure time: {time.strftime('%H:%M:%S', time.localtime(self.departure_time))}")

        # Wait until 5 seconds before departure for boarding
        boarding_start_time = self.departure_time - 5
        while time.time() < boarding_start_time:
            time.sleep(1)

        print(f"Boarding for flight {self.flight_number} at Gate {self.gate_id} has started.")

        # Final boarding call
        time.sleep(3)  # Simulate time for boarding to proceed
        print(f"Final boarding call for flight {self.flight_number} at Gate {self.gate_id}.")

        # Let passengers board
        while not self.airport.gates_queues[self.gate_id].empty():
            try:
                passenger = self.airport.gates_queues[self.gate_id].get_nowait()
                print(f"Passenger {passenger.name} boarded flight {self.flight_number}.")
                self.airport.gates_queues[self.gate_id].task_done()
            except Empty:
                break
        
        # Print departure details
        print(f"Flight {self.flight_number} is departing from Gate {self.gate_id}.")
