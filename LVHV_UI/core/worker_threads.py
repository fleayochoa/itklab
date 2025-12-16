from PyQt6.QtCore import QThread, pyqtSignal
from LVHV_UI.utils import config
#from LVHV_UI.core.pico_manager import PicoManager
import numpy as np
import time
import math

class DataThread(QThread):
    new_data = pyqtSignal(list)
    def __init__(self, sample_rate=config.SAMPLE_RATE, 
                 plot_rate=config.PLOT_RATE, 
                 num_channels=config.NUM_CHANNELS,
                  total_time=config.TOTAL_TIME,
                  parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.plot_rate = plot_rate
        self.num_channels = num_channels
        self.total_time = total_time
        self.samples_per_plot = self.sample_rate // self.plot_rate
        self.total_samples = self.total_time * self.sample_rate
        self.sample_counter = 0
        self.window_counter = 1
        self.values_buffer = np.zeros((self.num_channels, self.samples_per_plot))
        self.running = True
        self.started = False
        #self.picologger = PicoManager()
    def run(self):
        t = 0
        #self.picologger.initialize_device()
        while self.running:
            values = [
                math.sin(t),           # canal 1
                math.cos(t * 0.7),     # canal 2
                0.5*math.sin(2*t),      # canal 3
                0.5,                # canal 4
                0.2*math.sin(0.5*t),   # canal 5
                0.1*math.cos(3*t),    # canal 6
                0.7,               # canal 7
                0.3*math.sin(t),      # canal 8
                0.4*math.cos(t),     # canal 9
                0.6*math.sin(1.5*t),  # canal 10
                0.2,               # canal 11
                -0.7            # canal 12
            ][:self.num_channels]
            
            for i in range(self.num_channels):
                self.values_buffer[i][self.sample_counter] = values[i]
            if self.started:
                t += 1 / self.sample_rate
                self.sample_counter += 1
                self.sample_counter %= self.samples_per_plot

                if self.sample_counter >= self.samples_per_plot-1:
                    means = np.mean(self.values_buffer, axis=1)
                    self.new_data.emit(means.tolist())
            time.sleep(1 / self.sample_rate)

    def data_start(self):
        self.started = True
        self.sample_counter = 0
        self.window_counter = 1
        print("Inciando adquisición de datos...")
    def data_stop(self):
        self.started = False
        print("Deteniendo adquisición de datos...")