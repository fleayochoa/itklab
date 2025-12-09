from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QStackedLayout, QLineEdit
from PyQt6.QtCore import Qt
from LVHV_UI.utils import config
from LVHV_UI.ui.realtime_plotter import RealTimePlotter
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gráfico en tiempo real")

        #center = QWidget()
        #self.setCentralWidget(center)
        self.stack = QStackedLayout()
        container = QWidget()
        container.setLayout(self.stack)
        self.setCentralWidget(container)
        #layout = QVBoxLayout(center)
        self.plotter = RealTimePlotter(num_channels=config.NUM_CHANNELS,
                                       total_time=config.TOTAL_TIME,
                                       plot_rate=config.PLOT_RATE)

        #layout.addWidget(self.plotter)
        self.page_intro = QWidget()
        intro_layout = QVBoxLayout()
        self.label_intro = QLabel("Introduce el nombre de la medición:")
        self.input_text = QLineEdit()
        self.btn_continuar = QPushButton("Continuar")
        self.btn_continuar.clicked.connect(self.on_continue)
        intro_layout.addWidget(self.label_intro)
        intro_layout.addWidget(self.input_text)
        intro_layout.addWidget(self.btn_continuar)
        self.page_intro.setLayout(intro_layout)
        self.stack.addWidget(self.page_intro)
        # Botones y control
        self.page_controls = QWidget()
        self.hlayout = QVBoxLayout()
        self.btn_zoom_in = QPushButton("Zoom +")
        self.btn_zoom_out = QPushButton("Zoom -")
        self.btn_auto_range = QPushButton("Auto Range")
        self.slider_x_range = QSlider()
        self.slider_x_range.setOrientation(Qt.Orientation.Horizontal)
        self.slider_x_range.setMinimum(1)
        self.slider_x_range.setValue(1)
        self.slider_x_range.setMaximum(100)
        self.slider_x_range.setValue(100)
        self.slider_y_range = QSlider()
        self.slider_y_range.setOrientation(Qt.Orientation.Horizontal)
        self.slider_y_range.setMinimum(1)
        self.slider_y_range.setValue(1)
        self.slider_y_range.setMaximum(100)
        self.slider_y_range.setValue(100)

        # Conectar botones
        self.btn_zoom_in.clicked.connect(self.plotter.zoom_in)
        self.btn_zoom_out.clicked.connect(self.plotter.zoom_out)
        self.btn_auto_range.clicked.connect(self.plotter.set_auto_range)
        # Agregar al layout
        self.hlayout.addWidget(self.plotter)
        self.hlayout.addWidget(self.btn_zoom_in)
        self.hlayout.addWidget(self.btn_zoom_out)
        self.hlayout.addWidget(self.btn_auto_range)
        self.hlayout.addWidget(QLabel("X Range"))
        self.hlayout.addWidget(self.slider_x_range)
        self.hlayout.addWidget(QLabel("Y Range"))
        self.hlayout.addWidget(self.slider_y_range)
        self.page_controls.setLayout(self.hlayout)
        self.stack.addWidget(self.page_controls)
        #layout.addLayout(self.hlayout)

        self.stack.setCurrentWidget(self.page_intro)


    def on_new_data(self, new_values):
        self.plotter.update_plot(new_values)
    
    def on_data_finished(self):
        self.plotter.finish_plot()
        print("Data acquisition finished.")

    def on_continue(self):
        self.stack.setCurrentIndex(1)
