# monitor.py

import threading
import time
from collections import defaultdict
import csv 
import os

class Monitor:
    def __init__(self, 
                 airport, 
                 export_timeseries_data=False
                ):
        
        self.airport = airport
        self.export_timeseries_data = export_timeseries_data
        self.usage_stats = {
            "counters": defaultdict(int),
            "security": defaultdict(int),
            "gates": defaultdict(int),
            "shops": defaultdict(int),
            "taxis_city_to_airport": defaultdict(int),
            "taxis_airport_to_city": defaultdict(int),
        }
        self.total_entities = {
            "counters": len(airport.counters),
            "security": len(airport.security_lines),
            "gates": len(airport.gates),
            "shops": len(airport.shops),
            "taxis": len(airport.taxis),
        }
        self.lock = threading.Lock()
        self.monitoring = threading.Event()
        self.monitoring.set()

        # Timeseries data storage
        self.timeseries_data = []  # List to store data over time
        self.timeseries_lock = threading.Lock()

    def increment_usage(self, station_type, station_id):
        """Increment usage stats for a specific station."""
        with self.lock:
            self.usage_stats[station_type][station_id] += 1
            # Notify the GUI monitor
            self.airport.gui_monitor.enqueue_update(station_type)

    def decrement_usage(self, station_type, station_id):
        """Decrement usage stats for a specific station."""
        with self.lock:
            if self.usage_stats[station_type][station_id] > 0:
                self.usage_stats[station_type][station_id] -= 1
                self.airport.gui_monitor.enqueue_update(station_type)

    def start_monitoring(self):
        """Start monitoring usage stats and dynamic scaling."""
        threading.Thread(target=self.log_usage_stats, daemon=True).start()
        threading.Thread(target=self.monitor_usage, daemon=True).start()

    def monitor_usage(self):
        """Monitor the usage, add/remove entities, and collect timeseries data."""
        while self.monitoring.is_set():
            time.sleep(1) 
            timestamp = time.time()
            with self.lock:
                # Collect current usage stats
                current_stats = {}
                for station_type in self.usage_stats:
                    total = self.total_entities.get("taxis", 0) if "taxis" in station_type else self.total_entities.get(station_type, 0)
                    used = sum(self.usage_stats[station_type].values())
                    usage_percentage = (used / total) * 100 if total > 0 else 0
                    current_stats[station_type] = usage_percentage

                    if station_type not in ["taxis_city_to_airport", "taxis_airport_to_city", "gates"]:
                        if usage_percentage > 90:
                            if self.airport.dynamic_scaling_enabled:
                                print(f"Usage for {station_type} exceeded 90%. Adding new entity.")
                                threading.Thread(target=self.airport.add_entity, args=(station_type,), daemon=True).start()
                        elif usage_percentage < 15:
                            if self.airport.dynamic_scaling_enabled:
                                print(f"Usage for {station_type} below 15%. Removing an entity.")
                                threading.Thread(target=self.airport.remove_entity, args=(station_type,), daemon=True).start()

                # Record timeseries data if enabled
                if self.export_timeseries_data:
                    with self.timeseries_lock:
                        data_point = {
                            "timestamp": timestamp,
                            "total_passengers": self.airport.total_passengers,
                            "aircraft_waiting": len(self.airport.aircraft_queue.queue) + len(self.airport.active_aircrafts),
                            **current_stats
                        }
                        self.timeseries_data.append(data_point)

    def log_usage_stats(self):
        while self.monitoring.is_set():
            time.sleep(10)  
            with self.lock:
                print("\n--- Usage Statistics ---")
                for station_type, stats in self.usage_stats.items():
                    print(f"{station_type.capitalize()}:")
                    for station_id, count in stats.items():
                        print(f"  Station {station_id}: {count} uses")
                print("------------------------")

    def stop_monitoring(self):
        """Stop the monitoring."""
        self.monitoring.clear()

        if self.export_timeseries_data:
            self.export_data()

    def export_data(self, filename="timeseries_data.csv"):
        """Export the timeseries data to a CSV file."""
        with self.timeseries_lock:
            if not self.timeseries_data:
                print("No timeseries data to export.")
                return

            fieldnames = ["timestamp", "total_passengers", "aircraft_waiting"] + list(self.usage_stats.keys())

            # If the filename includes a directory, ensure the directory exists
            directory = os.path.dirname(filename)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # Write data to CSV
            try:
                with open(filename, mode="w", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for data_point in self.timeseries_data:
                        row = {key: data_point.get(key, 0) for key in fieldnames}
                        writer.writerow(row)
                print(f"Timeseries data exported to {filename}")
            except Exception as e:
                print(f"Failed to export timeseries data: {e}")
