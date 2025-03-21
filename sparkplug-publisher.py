import time
import json
import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import paho.mqtt.client as mqtt
from pysparkplug import NBirth, DBirth, Metric, DataType

class SparkplugPublisher:
    def __init__(self, group, edge_node, device, broker, port, username=None, password=None, use_tls=False):
        self.group = group
        self.edge_node = edge_node
        self.device = device
        self.client = mqtt.Client()

        if username and password:
            self.client.username_pw_set(username, password)

        if use_tls:
            self.client.tls_set()  # Use default TLS settings

        self.client.connect(broker, port, keepalive=60)
        self.client.loop_start()

    def topic(self, type):
        if type == "NBIRTH":
            return f"spBv1.0/{self.group}/NBIRTH/{self.edge_node}"
        elif type == "DBIRTH":
            return f"spBv1.0/{self.group}/DBIRTH/{self.edge_node}/{self.device}"

    def create_metrics(self, pressure, temperature, flowrate):
        timestamp = int(time.time() * 1000)
        return [
            Metric(name="Pressure", timestamp=timestamp, datatype=DataType.INT32, value=pressure, is_historical=False),
            Metric(name="Temperature", timestamp=timestamp, datatype=DataType.INT32, value=temperature, is_historical=False),
            Metric(name="FlowRate", timestamp=timestamp, datatype=DataType.INT32, value=flowrate, is_historical=False)
        ]

    def publish_nbirth(self):
        timestamp = int(time.time() * 1000)
        msg = NBirth(timestamp, 0, [])
        msg.edge_node_id = self.edge_node
        self.client.publish(self.topic("NBIRTH"), msg.encode(), qos=1, retain=True)

    def publish_dbirth(self, pressure, temperature, flowrate):
        timestamp = int(time.time() * 1000)
        metrics = self.create_metrics(pressure, temperature, flowrate)
        msg = DBirth(timestamp, 0, metrics)
        msg.edge_node_id = self.edge_node
        msg.device_id = self.device
        self.client.publish(self.topic("DBIRTH"), msg.encode(), qos=1, retain=True)

class SparkplugGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sparkplug Debugger to OI.MQTT")
        self.root.geometry("460x700")

        # Variables
        self.group_var = tk.StringVar(value="SolutionsPT")
        self.node_var = tk.StringVar(value="Production")
        self.device_var = tk.StringVar(value="Mixer1")
        self.broker_var = tk.StringVar(value="localhost")
        self.port_var = tk.IntVar(value=1883)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.use_tls_var = tk.BooleanVar()

        self.pressure_var = tk.IntVar(value=25)
        self.temperature_var = tk.IntVar(value=60)
        self.flowrate_var = tk.IntVar(value=200)

        self.auto_send = False

        # UI
        ttk.Label(root, text="Group ID:").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.group_var).pack()

        ttk.Label(root, text="Edge Node:").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.node_var).pack()

        ttk.Label(root, text="Device ID:").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.device_var).pack()

        ttk.Label(root, text="Broker Address:").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.broker_var).pack()

        ttk.Label(root, text="Port:").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.port_var).pack()

        ttk.Label(root, text="Username (optional):").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.username_var).pack()

        ttk.Label(root, text="Password (optional):").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.password_var, show="*").pack()

        ttk.Checkbutton(root, text="Use TLS (encrypted connection)", variable=self.use_tls_var).pack(pady=(10, 0))

        ttk.Label(root, text="\nMetric Values:").pack()
        ttk.Label(root, text="Pressure:").pack()
        ttk.Entry(root, textvariable=self.pressure_var).pack()
        ttk.Label(root, text="Temperature:").pack()
        ttk.Entry(root, textvariable=self.temperature_var).pack()
        ttk.Label(root, text="FlowRate:").pack()
        ttk.Entry(root, textvariable=self.flowrate_var).pack()

        # Action Buttons
        ttk.Button(root, text="Send NBIRTH", command=self.send_nbirth).pack(pady=10)
        ttk.Button(root, text="Send DBIRTH", command=self.send_dbirth).pack(pady=10)
        ttk.Button(root, text="Start Auto DBIRTH (5s)", command=self.start_auto_dbirth).pack(pady=5)
        ttk.Button(root, text="Stop Auto DBIRTH", command=self.stop_auto_dbirth).pack(pady=5)
        ttk.Button(root, text="Preview DBIRTH JSON", command=self.preview_dbirth).pack(pady=5)
        ttk.Button(root, text="Save Config", command=self.save_config).pack(pady=5)
        ttk.Button(root, text="Load Config", command=self.load_config).pack(pady=5)

        self.status = tk.StringVar()
        ttk.Label(root, textvariable=self.status, foreground="green").pack(pady=(10, 0))

    def get_publisher(self):
        return SparkplugPublisher(
            self.group_var.get(),
            self.node_var.get(),
            self.device_var.get(),
            self.broker_var.get(),
            self.port_var.get(),
            self.username_var.get() or None,
            self.password_var.get() or None,
            self.use_tls_var.get()
        )

    def get_metric_values(self):
        return self.pressure_var.get(), self.temperature_var.get(), self.flowrate_var.get()

    def send_nbirth(self):
        pub = self.get_publisher()
        pub.publish_nbirth()
        self.status.set("NBIRTH published ✅")

    def send_dbirth(self):
        pub = self.get_publisher()
        pressure, temperature, flowrate = self.get_metric_values()
        pub.publish_dbirth(pressure, temperature, flowrate)
        self.status.set("DBIRTH published ✅")

    def start_auto_dbirth(self):
        self.auto_send = True
        def loop():
            while self.auto_send:
                self.send_dbirth()
                time.sleep(5)
        threading.Thread(target=loop, daemon=True).start()
        self.status.set("Auto DBIRTH started 🔁")

    def stop_auto_dbirth(self):
        self.auto_send = False
        self.status.set("Auto DBIRTH stopped ⏹️")

    def preview_dbirth(self):
        pressure, temperature, flowrate = self.get_metric_values()
        data = {
            "Pressure": pressure,
            "Temperature": temperature,
            "FlowRate": flowrate
        }
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview DBIRTH Payload")
        preview_text = tk.Text(preview_window, height=10, width=50)
        preview_text.pack(padx=10, pady=10)
        preview_text.insert(tk.END, json.dumps(data, indent=2))

    def save_config(self):
        config = {
            "group": self.group_var.get(),
            "node": self.node_var.get(),
            "device": self.device_var.get(),
            "broker": self.broker_var.get(),
            "port": self.port_var.get(),
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "use_tls": self.use_tls_var.get(),
            "pressure": self.pressure_var.get(),
            "temperature": self.temperature_var.get(),
            "flowrate": self.flowrate_var.get(),
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.status.set("Configuration saved 💾")

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                config = json.load(f)
            self.group_var.set(config.get("group", ""))
            self.node_var.set(config.get("node", ""))
            self.device_var.set(config.get("device", ""))
            self.broker_var.set(config.get("broker", ""))
            self.port_var.set(config.get("port", 1883))
            self.username_var.set(config.get("username", ""))
            self.password_var.set(config.get("password", ""))
            self.use_tls_var.set(config.get("use_tls", False))
            self.pressure_var.set(config.get("pressure", 0))
            self.temperature_var.set(config.get("temperature", 0))
            self.flowrate_var.set(config.get("flowrate", 0))
            self.status.set("Configuration loaded 📂")

if __name__ == '__main__':
    root = tk.Tk()
    app = SparkplugGUI(root)
    root.mainloop()
