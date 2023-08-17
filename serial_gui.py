import tkinter as tk
import serial.tools.list_ports
import subprocess

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
        command = ["python", "data_visualization.py", selected_com_port]
        subprocess.run(command)
    except Exception as e:
        print(f"Error: {e}")

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

root.mainloop()
