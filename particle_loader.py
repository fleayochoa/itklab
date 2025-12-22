import minimalmodbus
import serial
import time
import csv
from datetime import datetime
import os

# --- CONFIGURACIÓN ---
PORT = 'COM3'  # Cambia esto por tu puerto
SLAVE_ADDRESS = 254
FILENAME = 'registro_particulas.csv' # Nombre del archivo donde se guardarán los datos
INTERVALO_SEGUNDOS = 60 # Frecuencia de guardado (ej. cada 60 segundos)

def setup_sensor():
    try:
        instrument = minimalmodbus.Instrument(PORT, SLAVE_ADDRESS)
        instrument.serial.baudrate = 115200
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.clear_buffers_before_each_transaction = True
        return instrument
    except Exception as e:
        print(f"Error conectando: {e}")
        exit()

def read_data(instr):
    try:
        # Leemos 14 registros empezando desde la dirección 0x03
        data = instr.read_registers(3, 14, functioncode=4)
        
        # Procesamos los datos (High byte + Low byte)
        return {
            "0.3um": (data[0] << 16) + data[1],
            "0.5um": (data[2] << 16) + data[3],
            "0.7um": (data[4] << 16) + data[5],
            "1.0um": (data[6] << 16) + data[7],
            "2.5um": (data[8] << 16) + data[9],
            "5.0um": (data[10] << 16) + data[11],
            "10.0um": (data[12] << 16) + data[13]
        }
    except IOError:
        print("Advertencia: No se pudo leer el sensor en este ciclo.")
        return None

def init_csv():
    file_exists = os.path.isfile(FILENAME)
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Fecha", "Hora", "0.3um", "0.5um", "0.7um", "1.0um", "2.5um", "5.0um", "10.0um"])
            print(f"Archivo {FILENAME} creado exitosamente.")

def log_to_csv(data):
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")
    
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            fecha, 
            hora, 
            data["0.3um"], 
            data["0.5um"], 
            data["0.7um"], 
            data["1.0um"], 
            data["2.5um"], 
            data["5.0um"], 
            data["10.0um"]
        ])
    print(f"[{hora}] Datos guardados -> 0.3um: {data['0.3um']} | 2.5um: {data['2.5um']}")

# --- PROGRAMA PRINCIPAL ---
if __name__ == "__main__":
    sensor = setup_sensor()
    init_csv()
    
    # Aseguramos que el sensor esté midiendo (Start detection)
    try:
        sensor.write_register(6, 1, functioncode=6)
        print("Sensor activado. Comenzando registro...")
    except IOError:
        print("Error al intentar activar el sensor.")

    try:
        while True:
            valores = read_data(sensor)
            
            if valores:
                log_to_csv(valores)
            
            # Cuenta regresiva para la siguiente medición
            time.sleep(INTERVALO_SEGUNDOS)
            
    except KeyboardInterrupt:
        print("\nDeteniendo script...")
        # Opcional: Detener el sensor al cerrar
        # sensor.write_register(6, 0, functioncode=6)
        print("Finalizado.")