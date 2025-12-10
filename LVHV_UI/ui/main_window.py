from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, 
    QStackedLayout, QLineEdit, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from LVHV_UI.utils import config
from LVHV_UI.ui.realtime_plotter import RealTimePlotter
from LVHV_UI.utils.utils import PloterStatus
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    start = pyqtSignal()    
    xlsx_name = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gráfico en tiempo real")

        self.stack = QStackedLayout()
        container = QWidget()
        container.setLayout(self.stack)
        self.setCentralWidget(container)
        self.plotter = RealTimePlotter(num_channels=config.NUM_CHANNELS,
                                       total_time=config.TOTAL_TIME,
                                       plot_rate=config.PLOT_RATE)
        self.plotter.stop_plot_signal.connect(self.on_data_finished)
        #layout.addWidget(self.plotter)
        self.page_intro = QWidget()
        intro_layout = QVBoxLayout()
        self.label_intro = QLabel("Introduce el nombre de la medición:")
        self.input_text = QLineEdit()
        self.btn_continuar = QPushButton("Continuar")
        self.btn_open_xlsx = QPushButton("Abrir XLSX")
        self.btn_open_xlsx.clicked.connect(self.open_xlsx_file)
        self.btn_continuar.clicked.connect(self.on_continue)
        intro_layout.addWidget(self.label_intro)
        intro_layout.addWidget(self.input_text)
        intro_layout.addWidget(self.btn_continuar)
        intro_layout.addWidget(self.btn_open_xlsx)
        self.page_intro.setLayout(intro_layout)
        self.stack.addWidget(self.page_intro)
        # Botones y control
        self.page_controls = QWidget()
        self.plot_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()
        self.control_layout = QVBoxLayout()
        self.play_layout = QVBoxLayout()
        self.play_button = QPushButton("Iniciar")
        self.pause_button = QPushButton("Pausar")
        self.stop_button = QPushButton("Detener")
        self.save_button = QPushButton("Guardar")
        self.reset_button = QPushButton("Reiniciar")
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

        # Conectar botones y sliders
        self.btn_zoom_in.clicked.connect(self.plotter.zoom_in)
        self.btn_zoom_out.clicked.connect(self.plotter.zoom_out)
        self.btn_auto_range.clicked.connect(self.plotter.set_auto_range)
        self.play_button.clicked.connect(self.on_start)
        self.pause_button.clicked.connect(self.on_pause)
        self.stop_button.clicked.connect(self.on_stop)
        self.reset_button.clicked.connect(self.on_reset)
        self.save_button.clicked.connect(self.on_save)
        self.slider_x_range.valueChanged.connect(self.plotter.slider_time)
        self.slider_y_range.valueChanged.connect(self.plotter.slider_voltage)
        # Agregar al layout
        self.plot_layout.addWidget(self.plotter)
        self.control_layout.addWidget(self.btn_zoom_in)
        self.control_layout.addWidget(self.btn_zoom_out)
        self.control_layout.addWidget(self.btn_auto_range)
        self.control_layout.addWidget(QLabel("X Range"))
        self.control_layout.addWidget(self.slider_x_range)
        self.control_layout.addWidget(QLabel("Y Range"))
        self.control_layout.addWidget(self.slider_y_range)
        self.play_layout.addWidget(self.play_button)
        self.play_layout.addWidget(self.pause_button)
        self.play_layout.addWidget(self.stop_button)
        self.play_layout.addWidget(self.reset_button)
        self.play_layout.addWidget(self.save_button)
        self.bottom_layout.addLayout(self.play_layout)
        self.bottom_layout.addLayout(self.control_layout)
        self.plot_layout.addLayout(self.bottom_layout)
        self.page_controls.setLayout(self.plot_layout)
        self.stack.addWidget(self.page_controls)
        #layout.addLayout(self.hlayout)

        self.stack.setCurrentWidget(self.page_intro)


    def on_new_data(self, new_values):
        self.plotter.update_plot(new_values)
    
    def on_data_finished(self):
        print("Data acquisition finished.")
        self.update_buttons()

    def on_continue(self):
        self.on_start()
        self.stack.setCurrentIndex(1)
        self.update_buttons()

    def on_stop(self):
        self.plotter.stop_plot()
        self.update_buttons()
    
    def on_pause(self):
        self.plotter.pause_plot()
        self.update_buttons()

    def on_start(self):
        self.start.emit()
        self.plotter.start_plot()
        self.update_buttons()
    
    def on_reset(self):
        self.plotter.reset_plot()
        self.update_buttons()
        self.input_text.setText("")
        self.stack.setCurrentWidget(self.page_intro)

    def on_save(self):
        self.plotter.save_plot(self.input_text.text())

    def update_buttons(self):
        if self.plotter.ploter_status == PloterStatus.RUNNING:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        elif self.plotter.ploter_status == PloterStatus.PAUSED:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:  # STOPPED
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def open_xlsx_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo CSV",
            "",
            "XLSX Files (*.xlsx)"     # ← FILTRO SOLO XLSX
        )
        