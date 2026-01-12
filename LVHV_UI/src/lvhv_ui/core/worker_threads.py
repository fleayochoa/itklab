from PyQt6.QtCore import QThread, pyqtSignal
from lvhv_ui.utils import config
from lvhv_ui.core.pico_manager import PicoManager
import numpy as np
import time
import math

class DataThread(QThread):
    new_data = pyqtSignal(list)
    def __init__(self, sample_rate=config.SAMPLE_RATE, 
                 plot_rate=config.PLOT_RATE,
                  parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.plot_rate = plot_rate
        self.running = True
        self.started = False
        self.pico_started = False
        self.picologger = PicoManager()
    def run(self):
        t = 0
        self.picologger.initialize_device()
        try:
            while self.running:
                if self.started:
                    if self.pico_started == False:
                        print("Iniciando adquisición en PicoLogger...")
                        self.pico_started = True
                        self.picologger.set_interval()
                    real_values =self.picologger.get_acquisition_data()
                    t += 1 / self.sample_rate
                    self.new_data.emit(real_values.tolist())
                time.sleep(1 / self.plot_rate) # Comentar
        finally:
            self.picologger.close_device()

    def data_start(self):
        self.started = True
        self.pico_started = False
        self.window_counter = 1
        print("Inciando adquisición de datos...")
    def data_stop(self):
        self.started = False
        print("Deteniendo adquisición de datos...")
    def close(self):
        print("Cerrando DataThread...")
        self.started = False
        self.running = False

        if self.picologger is not None:
            self.picologger.close_device()

        self.wait()  # espera a que run() termine
        print("DataThread cerrado correctamente")