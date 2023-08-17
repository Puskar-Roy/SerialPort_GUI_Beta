import tkinter as tk
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import csv
import threading
import sys
import subprocess
from queue import Queue

# Function to read Bluetooth data and store it in CSV
def read_bluetooth_data(port, data_queue, baud_rate=9600, timeout=1):
    bluetooth_serial = None
    try:
        bluetooth_serial = serial.Serial(port, baud_rate, timeout=timeout)
        
        while True:
            data = bluetooth_serial.readline().decode().strip()
            if data.startswith("$:"):
                parts = data.split(':')[1].split(',')
                if len(parts) >= 3:
                    gyro_x = float(parts[0])
                    gyro_y = float(parts[1])
                    gyro_z = float(parts[2])
                    accel_x = float(parts[3])
                    accel_y = float(parts[4])
                    accel_z = float(parts[5])
                    mag_x = float(parts[6])
                    mag_y = float(parts[7])
                    mag_z = float(parts[8])
                    
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Store data in CSV file
                    with open('data.csv', 'a', newline='') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([current_time, gyro_x, gyro_y, gyro_z])
                    
                    # Put data in the queue
                    data_queue.put((gyro_x, gyro_y, gyro_z))
    
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping the program.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if bluetooth_serial:
            bluetooth_serial.close()

# GUI part
class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth Data Visualization")
        
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        self.y_vals_x = []
        self.y_vals_y = []
        self.y_vals_z = []
        
        self.data_queue = Queue()
        self.data_reader_thread = threading.Thread(target=read_bluetooth_data, args=(bluetooth_port, self.data_queue))
        self.data_reader_thread.start()
        
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=1)
    
    def update_plot(self, i):
        while not self.data_queue.empty():
            gyro_x, gyro_y, gyro_z = self.data_queue.get()
            self.y_vals_x.append(gyro_x)
            self.y_vals_y.append(gyro_y)
            self.y_vals_z.append(gyro_z)
            
            if len(self.y_vals_x) > 120:
                self.y_vals_x.pop(0)
                self.y_vals_y.pop(0)
                self.y_vals_z.pop(0)
            
            self.ax.clear()
            self.ax.plot(self.y_vals_x, label='Gyro X-axis', color='blue')
            self.ax.plot(self.y_vals_y, label='Gyro Y-axis', color='green')
            self.ax.plot(self.y_vals_z, label='Gyro Z-axis', color='red')
            
            self.ax.set_ylabel("Gyro Data")
            self.ax.set_xlabel("Time")
            self.ax.set_title("Gyro Data Graph")
            self.ax.legend()

# Show COM ports in dropdown and connect button
def show_active_com_ports():
    available_ports = serial.tools.list_ports.comports()
    com_port_list = []
    for port in available_ports:
        com_port_list.append(port.device)
    return com_port_list

def connect_to_com_port():
    selected_com_port = com_port_var.get()
    try:
        root.destroy()
        command = ["python", "combined_script.py", selected_com_port]
        subprocess.run(command)
    except Exception as e:
        print(f"Error: {e}")

# Main
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Serial Port Connector")
    
    com_port_var = tk.StringVar(root)
    com_port_var.set("Select COM Port")  # Default value for dropdown
    
    com_port_label = tk.Label(root, text="Select COM Port:")
    com_port_label.pack()
    
    com_port_dropdown = tk.OptionMenu(root, com_port_var, *show_active_com_ports())
    com_port_dropdown.pack()
    
    connect_button = tk.Button(root, text="Connect", command=connect_to_com_port)
    connect_button.pack()
    
    bluetooth_port = None
    
    root.mainloop()
