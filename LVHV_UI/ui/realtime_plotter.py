from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
import pyqtgraph.exporters
import pyqtgraph as pg
import numpy as np
from datetime import timedelta


class RealTimePlotter(QWidget):
    def __init__(self, num_channels,total_time, plot_rate, parent=None):
        super().__init__(parent)
        self.num_channels = num_channels
        self.total_time = total_time
        self.buffer_size = int(total_time * plot_rate)
        self.plot_rate = plot_rate
        layout = QVBoxLayout(self)
        # Crear plot
        self.plot_widget = pg.PlotWidget()
        # Apariencia del plot
        self.plot_widget.setBackground('white')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Voltaje', units='V')
        self.plot_widget.setLabel('bottom', 'Tiempo', units='s')
        colors = ['yellow', 'cyan', 'magenta', 'green', 'red']
        self.curves = []
        # Línea para actualizar en tiempo real
        for i in range(self.num_channels):
            self.curves.append(
                self.plot_widget.plot(
                    pen=pg.mkPen(color=colors[i % len(colors)], width=2)
                )
            )
        # Agregar al layout
        layout.addWidget(self.plot_widget)
        # Buffer local (temporal)
        self.x_data = np.linspace(0, self.total_time, self.buffer_size)
        self.y_data = np.zeros((self.num_channels, self.buffer_size))
        self.array_index = 0
        self.time_elapsed = 0
        self.dt = 1 / self.plot_rate

        # Actualizar grafico
    def update_plot(self, new_value):
        for ch in range(self.num_channels):
            self.y_data[ch][self.array_index] = new_value[ch]

        self.array_index = (self.array_index + 1)
        self.time_elapsed += self.dt
        
        # Actualizar la curva
        for ch in range(self.num_channels):
            self.curves[ch].setData(
                x=self.x_data,
                y=self.y_data[ch]
            )
    
    def set_auto_range(self):
        self.plot_widget.setXRange(0,self.time_elapsed) 

    def zoom_in(self):
        self.plot_widget.getViewBox().scaleBy((0.9, 0.9))

    def zoom_out(self):
        self.plot_widget.getViewBox().scaleBy((1.1, 1.1))

    def finish_plot(self):
        self.set_auto_range()
        time_strings = [str(timedelta(seconds=int(t))) for t in self.x_data]
        time_col = np.array(time_strings).reshape(-1, 1)
        arr = np.array(self.y_data).T.round(4)
        arr_full = np.hstack((time_col, arr))[:-1]
        exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
        exporter.export("plot.png")
        header = "TIME," + ",".join([f"CH{i}" for i in range(len(self.y_data))])
        np.savetxt("test.csv", arr_full,fmt="%s" ,delimiter=",", header=header, comments="")
    
