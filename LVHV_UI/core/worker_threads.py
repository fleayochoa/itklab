from PyQt6.QtCore import QThread, pyqtSignal
from LVHV_UI.utils import config
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
    def run(self):
        t = 0
        while self.running:
            values = [
                math.sin(t),           # canal 1
                math.cos(t * 0.7),     # canal 2
                0.5*math.sin(2*t)      # canal 3
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


            time.sleep(1 / self.sample_rate)  # ~100 Hz
    def data_start(self):
        self.started = True
        self.sample_counter = 0
        self.window_counter = 1
        print("Inciando adquisición de datos...")
    def data_stop(self):
        self.started = False
        print("Deteniendo adquisición de datos...")