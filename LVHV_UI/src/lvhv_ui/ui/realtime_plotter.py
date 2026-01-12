from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
import pyqtgraph.exporters
from lvhv_ui.utils.utils import PloterStatus
import pyqtgraph as pg
import numpy as np
from datetime import timedelta
from pathlib import Path
from lvhv_ui.utils import config



class RealTimePlotter(QWidget):
    stop_plot_signal = pyqtSignal(list)
    def __init__(self, num_channels,total_time, plot_rate, file_name = "test",parent=None, sample_rate=1000):
        super().__init__(parent)
        self.ploter_status = PloterStatus.STOPPED
        self.num_channels = num_channels
        self.total_time = total_time
        self.buffer_size = int(total_time * sample_rate)
        self.plot_rate = plot_rate
        self.sample_rate = sample_rate
        self.file_name = file_name
        self.save_path = ""
        layout = QVBoxLayout(self)
        # Crear plot
        self.plot_widget = pg.PlotWidget()
        # Apariencia del plot
        self.plot_widget.setBackground('white')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Voltaje', units='V')
        self.plot_widget.setLabel('bottom', 'Tiempo', units='s')
        colors = ['yellow', 'cyan', 'magenta', 'green', 'red', 'black']
        self.curves = []
        # Línea para actualizar en tiempo real
        for i in range(self.num_channels):
            self.curves.append(
                self.plot_widget.plot(
                    pen=pg.mkPen(color=colors[i % len(colors)], width=2),
                    name=config.channel_names[i+1]
                )
            )
        # Agregar al layout
        layout.addWidget(self.plot_widget)
        # Buffer local (temporal)
        self.x_data = np.linspace(0, self.total_time, self.buffer_size)
        self.seconds_data = np.linspace(0, self.total_time-1, self.total_time)
        self.y_data = np.zeros((self.num_channels, self.buffer_size))
        self.csv_data = np.zeros((self.num_channels, self.total_time))  
        self.array_index = 0
        self.time_elapsed = 0
        self.seconds_elapsed = 0
        self.dt = 1 / self.plot_rate
        self.counter_ticks = 0 # El csv guarda a 1Hz

        # Actualizar grafico
    def update_plot(self, new_values):
        if self.ploter_status != PloterStatus.RUNNING:
            return
        
        for j in range(len(new_values[0])):
            for ch in range(self.num_channels):
                self.y_data[ch][self.array_index] = new_values[ch][j]
            self.array_index += 1
            self.counter_ticks += 1
        self.time_elapsed += self.dt*len(new_values[0])
        
        # Actualizar la curva
        for ch in range(self.num_channels):
            self.curves[ch].setData(
                x=self.x_data,
                y=self.y_data[ch]
            )

        # Detener plot (finalizado)
        if self.array_index >= self.buffer_size:
            self.csv_data = self.get_csv_data()
            print(self.counter_ticks, self.seconds_elapsed, self.total_time)
            self.ploter_status = PloterStatus.STOPPED
            data_str = ["_".join(f'{x:.2f}' for x in fila) for fila in self.csv_data[:, -5:].transpose()]
            self.stop_plot_signal.emit(data_str)
            self.finish_plot()
    
    def get_csv_data(self):
        N = self.array_index
        N_trunc = (N//config.SAMPLE_RATE)*config.SAMPLE_RATE
        data_trunc = self.y_data[:, :N_trunc]
        data_reshaped = data_trunc.reshape(self.num_channels, -1, config.SAMPLE_RATE)
        data_1Hz = data_reshaped.mean(axis=2)
        return data_1Hz
    
    def set_auto_range(self):
        self.plot_widget.setXRange(0,self.time_elapsed, padding=0) 

    def set_max_range(self):
        self.plot_widget.setXRange(0,self.total_time, padding=0) 
        self.plot_widget.setYRange(-10,10, padding=0)

    def start_plot(self):
        if self.ploter_status != PloterStatus.RUNNING:
            if self.ploter_status == PloterStatus.STOPPED:
                self.array_index = 0
                self.time_elapsed = 0
                self.y_data = np.zeros((self.num_channels, self.buffer_size))
                for ch in range(self.num_channels):
                    self.curves[ch].setData(
                        x=self.x_data,
                        y=self.y_data[ch]
                    )
            else: 
                pass  # Resuming from PAUSED state
        self.ploter_status = PloterStatus.RUNNING

    def stop_plot(self):
        self.ploter_status = PloterStatus.STOPPED
        self.finish_plot()

    def pause_plot(self):
        self.ploter_status = PloterStatus.PAUSED

    def reset_plot(self):
        self.ploter_status = PloterStatus.STOPPED
        self.array_index = 0
        self.time_elapsed = 0
        self.seconds_elapsed = 0
        self.y_data = np.zeros((self.num_channels, self.buffer_size))
        for ch in range(self.num_channels):
            self.curves[ch].setData(
                x=self.x_data,
                y=self.y_data[ch]
            )
        self.plot_widget.setXRange(0, 10)
    
    def zoom_in(self):
        self.plot_widget.getViewBox().scaleBy((0.9, 0.9))

    def zoom_out(self):
        self.plot_widget.getViewBox().scaleBy((1.1, 1.1))

    def slider_time(self, value):
        xmin, xmax = self.plot_widget.getViewBox().viewRange()[0]   # eje X
        xcenter = (xmin + xmax) / 2
        new_width = self.total_time * (value / 100)
        self.plot_widget.setXRange(xcenter - new_width / 2, xcenter + new_width / 2)

    def slider_voltage(self, value):
        ymin, ymax = self.plot_widget.getViewBox().viewRange()[1]   # eje Y
        ycenter = (ymin + ymax) / 2
        new_height = 10 * (value / 100)
        self.plot_widget.setYRange(ycenter - new_height / 2, ycenter + new_height / 2)

    def finish_plot(self):
        self.ploter_status = PloterStatus.STOPPED
        self.set_auto_range()
        name = "recovery"
        self.save_plot(name)

    def set_filename(self, filename):
        self.file_name = filename
    
    def save_plot(self, filename=None):
        name = filename if filename else self.file_name
        time_strings = [str(timedelta(seconds=int(t))) for t in self.seconds_data]
        time_col = np.array(time_strings).reshape(-1, 1)
        arr = self.csv_data.T.round(4)
        arr_full = np.hstack((time_col, arr))
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        exporter.export(f"{name}.png")
        header = "TIME," + ",".join([f"CH{i+1}" for i in range(len(self.y_data))])
        filename = Path(self.save_path) / f"{name}.csv" if self.save_path != "" else f"{name}.csv"
        np.savetxt(filename, arr_full,fmt="%s" ,delimiter=",", header=header, comments="")