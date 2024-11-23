# monitor.py

import threading
import time
from collections import defaultdict


class Monitor:
    def __init__(self, airport):
        self.airport = airport
        self.usage_stats = {
            "counters": defaultdict(int),
            "security": defaultdict(int),
            "gates": defaultdict(int),
            "shops": defaultdict(int),
            "taxis_city_to_airport": defaultdict(int),  # Separate tracking for city_to_airport
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
        """Periodically log usage stats."""
        threading.Thread(target=self.log_usage_stats, daemon=True).start()

    def log_usage_stats(self):
        while self.monitoring.is_set():
            time.sleep(10)  # Log stats every 10 seconds
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

