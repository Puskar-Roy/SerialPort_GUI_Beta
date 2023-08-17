s
import subprocess

def show_active_com_ports():
    available_ports = serial.tools.list_ports.comports()
    com