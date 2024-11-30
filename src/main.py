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
    num_counters = 4
    num_security_lines = 5
    num_taxis = 15
    num_passengers = 100
    num_shops = 5
    num_gates = 7
    num_flights = 10
    
    dynamic_scaling_enabled = False
    export_timeseries_data = False

    # Create the Airport instance
    airport = Airport(
        num_counters=num_counters,
        num_taxis=num_taxis,
        num_security_lines=num_security_lines,
        num_passengers=num_passengers,
        num_shops=num_shops,
        num_gates=num_gates,
        num_flights=num_flights,
        dynamic_scaling_enabled=dynamic_scaling_enabled,
        export_timeseries_data=export_timeseries_data
    )

    # Run the simulation in a separate thread
    simulation_thread = threading.Thread(target=airport.start_simulation, daemon=True)
    simulation_thread.start()

    # Start the GUI in the main thread
    airport.gui_monitor.start()
        
    print("Simulation finished.")