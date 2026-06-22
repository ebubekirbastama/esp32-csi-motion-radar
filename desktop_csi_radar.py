import csv
import time
import datetime
import threading
import serial
import numpy as np
import tkinter as tk
from tkinter import ttk

DEFAULT_PORT = "COM5"
BAUD = 115200

class CSIRadarDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("EBS ESP32 CSI Radar Desktop")
        self.root.geometry("1000x650")
        self.root.configure(bg="#111111")

        self.running = False
        self.serial_connection = None
        self.variance_history = []
        self.log_rows = []

        self.threshold = 8.0

        self.setup_ui()

    def setup_ui(self):
        top = tk.Frame(self.root, bg="#1c1c1c")
        top.pack(fill=tk.X, padx=10, pady=10)

        self.start_button = ttk.Button(top, text="START", command=self.toggle)
        self.start_button.pack(side=tk.LEFT, padx=5)

        tk.Label(top, text="COM Port:", bg="#1c1c1c", fg="white").pack(side=tk.LEFT, padx=5)

        self.port_entry = tk.Entry(top, width=10)
        self.port_entry.insert(0, DEFAULT_PORT)
        self.port_entry.pack(side=tk.LEFT)

        tk.Label(top, text="Threshold:", bg="#1c1c1c", fg="white").pack(side=tk.LEFT, padx=5)

        self.threshold_entry = tk.Entry(top, width=8)
        self.threshold_entry.insert(0, str(self.threshold))
        self.threshold_entry.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            top,
            text="SYSTEM STOPPED",
            bg="#1c1c1c",
            fg="red",
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(side=tk.RIGHT, padx=20)

        info = tk.Frame(self.root, bg="#111111")
        info.pack(fill=tk.X, padx=10)

        self.rssi_label = tk.Label(info, text="RSSI: ---", bg="#111111", fg="#00ffcc", font=("Arial", 14))
        self.rssi_label.pack(side=tk.LEFT, padx=20)

        self.variance_label = tk.Label(info, text="Variance: ---", bg="#111111", fg="#00ffcc", font=("Arial", 14))
        self.variance_label.pack(side=tk.LEFT, padx=20)

        self.analysis_label = tk.Label(info, text="Analysis: ---", bg="#111111", fg="yellow", font=("Arial", 14, "bold"))
        self.analysis_label.pack(side=tk.LEFT, padx=20)

        columns = ("time", "rssi", "variance", "analysis")
        self.table = ttk.Treeview(self.root, columns=columns, show="headings", height=20)

        for column in columns:
            self.table.heading(column, text=column.upper())
            self.table.column(column, width=180)

        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        try:
            port = self.port_entry.get().strip()
            self.threshold = float(self.threshold_entry.get())

            self.serial_connection = serial.Serial(port, BAUD, timeout=1)
            self.running = True

            self.start_button.config(text="STOP")
            self.status_label.config(text="RADAR ACTIVE", fg="lime")

            threading.Thread(target=self.read_loop, daemon=True).start()

        except Exception as error:
            self.status_label.config(text=f"ERROR: {error}", fg="red")

    def stop(self):
        self.running = False
        self.start_button.config(text="START")
        self.status_label.config(text="SYSTEM STOPPED", fg="red")

        if self.serial_connection:
            self.serial_connection.close()

        self.save_log()

    def read_loop(self):
        while self.running:
            try:
                line = self.serial_connection.readline().decode(errors="ignore").strip()

                if not line or not line[0].isdigit():
                    continue

                parts = line.split(",")

                if len(parts) < 10:
                    continue

                rssi = float(parts[1])

                csi_values = []

                for value in parts[3:]:
                    try:
                        csi_values.append(float(value))
                    except ValueError:
                        pass

                if len(csi_values) < 10:
                    continue

                csi_array = np.array(csi_values)
                current_variance = float(np.std(csi_array))

                self.variance_history.append(current_variance)

                if len(self.variance_history) > 20:
                    self.variance_history.pop(0)

                average_variance = float(np.mean(self.variance_history))

                if average_variance > self.threshold:
                    analysis = "MOTION DETECTED"
                else:
                    analysis = "STABLE"

                now = datetime.datetime.now().strftime("%H:%M:%S")

                self.root.after(0, self.update_ui, now, rssi, average_variance, analysis)

                time.sleep(0.01)

            except Exception as error:
                self.root.after(
                    0,
                    lambda: self.status_label.config(text=f"READ ERROR: {error}", fg="red")
                )

    def update_ui(self, now, rssi, variance, analysis):
        self.rssi_label.config(text=f"RSSI: {rssi}")
        self.variance_label.config(text=f"Variance: {variance:.2f}")
        self.analysis_label.config(text=f"Analysis: {analysis}")

        if analysis == "MOTION DETECTED":
            self.status_label.config(text="MOTION DETECTED", fg="red")
        else:
            self.status_label.config(text="RADAR ACTIVE", fg="lime")

        row = (now, rssi, round(variance, 2), analysis)
        self.table.insert("", 0, values=row)
        self.log_rows.append(row)

        if len(self.table.get_children()) > 100:
            self.table.delete(self.table.get_children()[-1])

    def save_log(self):
        if not self.log_rows:
            return

        filename = f"ebs_csi_log_{int(time.time())}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "RSSI", "Variance", "Analysis"])
            writer.writerows(self.log_rows)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSIRadarDesktop(root)
    root.mainloop()
