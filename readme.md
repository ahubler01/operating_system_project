# OS Group Project

## Project Description

This project simulates the management of an international airport, focusing on the coordination and interaction of various entities such as aircraft, passengers, taxis, counters, security lines, shops, and gates. The simulation aims to model the dynamic and concurrent nature of airport operations using multithreading and synchronization mechanisms.

## Features

- Aircraft Management: Simulates flight scheduling, gate assignments, boarding, and departure processes.
- Passenger Flow: Models passenger behaviors from arrival at the airport to boarding the aircraft, including check-in, security checks, shopping, and gate boarding.
- Resource Allocation: Manages airport resources like taxis, check-in counters, security lines, shops, and gates, dynamically adjusting to the simulation's needs.
- Concurrency and Synchronization: Implements threading and synchronization to simulate concurrent activities and manage shared resources safely.
- Monitoring and Visualization: Includes a monitoring system and a GUI to track and visualize the status and usage of resources in real-time.

## Directory Structure:

```plaintext
src/
├── entities/
│   ├── __init__.py
│   ├── aircraft.py
│   ├── airport.py
│   ├── counter.py
│   ├── gates.py
│   ├── passenger.py
│   ├── security.py
│   ├── shops.py
│   └── taxi.py
├── main.py
├── gui_monitor.py
└── monitor.py
```

## Entities

- Aircraft (aircraft.py): Manages aircraft operations including gate assignments and flight departures.
- Airport (airport.py): Acts as the central hub coordinating all entities within the simulation.
- Counter (counter.py): Simulates the check-in process where passengers receive boarding passes.
- Gates (gates.py): Handles the boarding gates, managing passenger boarding procedures.
- Passenger (passenger.py): Represents individual passengers with behaviors and interactions in the airport.
- Security (security.py): Models security checkpoints that passengers must clear before proceeding to the gates.
- Shops (shops.py): Simulates retail shops where passengers can shop while waiting for their flights.
- Taxi (taxi.py): Manages the transportation of passengers to and from the airport.

## Getting Started:

Required Python libraries:

```
threading
queue
random
time
tkinter (for GUI)
```

To start the simulation, run:

```python
python main.py
```

## Configuration

You can adjust simulation parameters in main.py:

```python
if __name__ == "__main__":
    num_counters = 4
    num_security_lines = 5
    num_taxis = 45
    num_passengers = 150
    num_shops = 5
    num_gates = 7
    num_flights = 10

    dynamic_scaling_enabled = True
    export_timeseries_data = False
```

## Contributors:

- Armand Hubler
- Alejandra Hernandez
- Juan Carlos Vargas
- Felipe Gomez
- Mariano Delpree
