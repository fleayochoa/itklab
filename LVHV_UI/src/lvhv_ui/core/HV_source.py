import serial
import time
from serial.tools import list_ports
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class HVSource(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, port = None, baudrate: int = 9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.voltage = [0.0, 0.0]
        self.ramp_speed = [0, 0]
        self.connection = None
        self.send = False
    
    @staticmethod
    def get_available_ports():
        ports = list_ports.comports()
        str_data = ["{};{}".format(port.device, port.description) for port in ports]
        return str_data
    
    def set_ready_to_send(self):
        self.send = True

    def set_serial_params(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        print(f"Serial params set: Port {self.port}, Baudrate {self.baudrate}")

    def set_source_params(self, voltage_ch1, voltage_ch2, ramp_speed_ch1, ramp_speed_ch2):
        self.voltage = [voltage_ch1, voltage_ch2]
        self.ramp_speed = [ramp_speed_ch1, ramp_speed_ch2]
        print(f"Source params set: Voltages {self.voltage}, Ramp Speeds {self.ramp_speed}")

    def start_connection(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connection.write(b'\r\n')  # Send initial newline to wake up the device
            time.sleep(0.5)  # Wait for the connection to establish
            response = self.connection.readline().decode('ascii').strip()
            print(response)
            print("Connection established.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def send_command(self, command):
        try:
            full_command = command + '\r\n' # Add \r=<CR> and \n=<LF>
            cmd_ascii = full_command.encode('ascii')  # Convert commando to ascii
            self.connection.write(cmd_ascii) # Send command to HV Supply
            time.sleep(0.5) # Wait 0.5 seconds to recive the response
            response = self.connection.readline().decode('ascii').strip() # Read the response
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        
    def set_voltage(self, channel, voltage):
        if channel not in [1,2]:
            raise ValueError("Invalid Channel. Use 1 or 2")
        command = f"D{channel}={voltage:.2f}"
        self.send_command(command)
    
    def set_ramp_speed(self, channel, speed):
        if channel not in [1,2]:
            raise ValueError("Invalid Channel. Use 1 or 2")
        command = f"V{channel}={speed}"
        self.send_command(command)
    
    def apply_parameters(self, channel):
        if channel not in [1,2]:
            raise ValueError("Invalid Channel. Use 1 or 2")
        command = f"G{channel}"
        self.send_command(command)

    def run(self): # long running task
        while True:
            if self.send:
                self.send = False
                i=0
                for ch in [1,2]:
                    self.set_voltage(ch, self.voltage[ch-1])
                    i = i + 1
                    self.progress.emit(i)
                    self.set_ramp_speed(ch, self.ramp_speed[ch-1])
                    i = i + 1
                    self.progress.emit(i)
                    self.apply_parameters(ch)
                    i = i + 1
                    self.progress.emit(i)
                self.finished.emit()
            else:
                time.sleep(0.1)