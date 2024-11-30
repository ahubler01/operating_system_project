# gui_monitor.py

import tkinter as tk
from tkinter import ttk
import queue

class GUIMonitor:
    def __init__(self, 
                 monitor
                 ):
        
        self.monitor = monitor
        self.root = tk.Tk()
        self.root.title("Airport Usage Monitor")
        self.root.geometry("700x400")
        self.root.configure(bg="white")  

        self.update_queue = queue.Queue()

        self.tree = ttk.Treeview(
            self.root, 
            columns=("Type", "Usage (%)", "Total"), 
            show="headings", 
            height=15
        )
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Define table columns
        self.tree.heading("Type", text="Entity Type", anchor="center")
        self.tree.heading("Usage (%)", text="Usage (%)", anchor="center")
        self.tree.heading("Total", text="Total Entities", anchor="center")

        # Apply bold styling to the table headers
        style = ttk.Style(self.root)
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        # Configure column widths and alignment
        self.tree.column("Type", width=150, anchor="center")
        self.tree.column("Usage (%)", width=100, anchor="center")
        self.tree.column("Total", width=150, anchor="center")

    def enqueue_update(self, station_type):
        """Add an update to the queue."""
        self.update_queue.put(station_type)

    def process_updates(self):
        """Process all updates in the queue."""
        while not self.update_queue.empty():
            station_type = self.update_queue.get()
            self.update_gui()

    def update_gui(self):
        """Update the table with the latest usage stats."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_passengers = self.monitor.airport.total_passengers
        aircraft_waiting = len(self.monitor.airport.aircraft_queue.queue) + len(self.monitor.airport.active_aircrafts)

        self.tree.insert("", "end", values=("Total Passengers", total_passengers, ""))

        self.tree.insert("", "end", values=("Aircraft Waiting", aircraft_waiting, ""))

        self.tree.insert("", "end", values=("", "", ""))

        # Populate the table with summarized data
        for station_type, stats in self.monitor.usage_stats.items():
            if "taxis" in station_type:
                ride_type = station_type.replace("_", " ").capitalize()
                total = self.monitor.total_entities["taxis"]
                used = sum(stats.values())
                usage_percentage = (used / total) * 100 if total > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(ride_type, f"{usage_percentage:.2f}%", total)
                )
            else:
                # Other station types
                total = self.monitor.total_entities[station_type]
                used = sum(stats.values())
                usage_percentage = (used / total) * 100 if total > 0 else 0
                self.tree.insert(
                    "",
                    "end",
                    values=(station_type.capitalize(), f"{usage_percentage:.2f}%", total)
                )


    def periodic_update(self):
        """Periodically update the GUI using tkinter's thread-safe `after()` method."""
        self.process_updates()
        self.root.after(2000, self.periodic_update)  

    def start(self):
        """Start the GUI."""
        self.periodic_update() 
        self.root.mainloop()
        
    def stop(self):
        """Stop the GUI."""
        self.root.after(0, self.root.quit)
