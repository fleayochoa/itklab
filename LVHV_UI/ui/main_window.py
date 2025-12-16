from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, 
    QStackedLayout, QLineEdit, QHBoxLayout, QFileDialog, QListWidget, QComboBox
)
from PyQt6.QtMultimedia import QSoundEffect

from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from LVHV_UI.utils import config
from LVHV_UI.ui.realtime_plotter import RealTimePlotter
from LVHV_UI.utils.utils import PloterStatus, XLSXLoader
import pyqtgraph as pg
import numpy as np
import pandas as pd

class MainWindow(QMainWindow):
    start = pyqtSignal()    
    xlsx_name = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gráfico en tiempo real")

        self.xlsx_loader = XLSXLoader()

        self.alarma = QSoundEffect()
        self.alarma.setSource(QUrl.fromLocalFile("alarma.wav"))
        self.alarma.setVolume(0.8)
        self.file_name = "no_name"
        self.stack = QStackedLayout()
        container = QWidget()
        container.setLayout(self.stack)
        self.setCentralWidget(container)
        self.plotter = RealTimePlotter(num_channels=config.NUM_CHANNELS,
                                       total_time=config.TOTAL_TIME,
                                       plot_rate=config.PLOT_RATE)
        self.plotter.stop_plot_signal.connect(self.on_data_finished)
        #layout.addWidget(self.plo  tter)
        self.page_intro = QWidget()
        intro_layout = QVBoxLayout()
        self.left_xlsx = QVBoxLayout()
        self.right_xlsx = QVBoxLayout()
        self.xlsx_container = QHBoxLayout()
        self.label_intro = QLabel("Introduce el nombre de la medición:")
        self.btn_continuar = QPushButton("Continuar")
        self.btn_continuar.setEnabled(False)
        self.btn_open_xlsx = QPushButton("Abrir XLSX")
        self.left_list_xlsx = QComboBox()
        self.left_list_pogo = QComboBox()
        self.right_list_xlsx = QComboBox()
        self.right_list_pogo = QComboBox()
        self.left_list_pogo.addItems([str(pin) for pin in config.pogo_pins])
        self.right_list_pogo.addItems([str(pin) for pin in config.pogo_pins])
        self.btn_open_xlsx.clicked.connect(self.open_xlsx_file)
        self.btn_continuar.clicked.connect(self.on_continue)
        intro_layout.addWidget(self.label_intro)
        intro_layout.addWidget(self.btn_continuar)
        intro_layout.addWidget(self.btn_open_xlsx)
        intro_layout.addLayout(self.xlsx_container)
        self.xlsx_container.addLayout(self.left_xlsx)
        self.xlsx_container.addLayout(self.right_xlsx)
        self.left_xlsx.addWidget(self.left_list_xlsx)
        self.left_xlsx.addWidget(self.left_list_pogo)
        self.right_xlsx.addWidget(self.right_list_xlsx)
        self.right_xlsx.addWidget(self.right_list_pogo)
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
        self.btn_max_range = QPushButton("Max Range")
        self.data_selector = QComboBox()
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
        self.btn_max_range.clicked.connect(self.plotter.set_max_range)
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
        self.control_layout.addWidget(self.btn_max_range)
        self.control_layout.addWidget(QLabel("X Range"))
        self.control_layout.addWidget(self.slider_x_range)
        self.control_layout.addWidget(QLabel("Y Range"))
        self.control_layout.addWidget(self.slider_y_range)
        self.control_layout.addWidget(QLabel("Seleccionar dato:"))
        self.control_layout.addWidget(self.data_selector)
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
    
    def on_data_finished(self, data):
        print("Data acquisition finished.")
        self.alarma.play()
        self.update_buttons()
        self.data_selector.clear()
        self.data_selector.addItems(data)

    def on_continue(self):
        self.on_start()
        self.stack.setCurrentIndex(1)
        self.file_name = "{}-{} {}-{}".format(self.left_list_xlsx.currentText()[-4:], 
                        self.left_list_pogo.currentText(),
                        self.right_list_xlsx.currentText()[-4:],
                        self.right_list_pogo.currentText())
        self.plotter.set_filename(self.file_name)
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
        self.stack.setCurrentWidget(self.page_intro)
        self.update_xlsx()

    def on_save(self):
        self.plotter.save_plot()
        self.xlsx_loader.overwrite_xlsx(
            self.data_selector.currentText(),
            [self.left_list_xlsx.currentText(), self.right_list_xlsx.currentText()],
            [self.left_list_pogo.currentText(), self.right_list_pogo.currentText()]
        )
        print("guardado con exito")
        #self.selected_index = 
        #self.left_data_dict = {"PP Board Used": self.left_list_pogo.currentText(),
        #                       "VIN+": self.}

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
        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo CSV",
            "",
            "XLSX Files (*.xlsx)"     # ← FILTRO SOLO XLSX
        )
        self.update_xlsx()

    def update_xlsx(self):
        self.xlsx_loader.set_file_path(self.file_path)
        self.xlsx_loader.load_data()
        ids_con_ntc_vacio = self.xlsx_loader.get_ids_with_empty_ntc()
        self.left_list_xlsx.clear()
        self.right_list_xlsx.clear()
        self.left_list_xlsx.addItems(ids_con_ntc_vacio)
        self.right_list_xlsx.addItems(ids_con_ntc_vacio)
        if len(ids_con_ntc_vacio) > 0:
            self.left_list_xlsx.setCurrentIndex(0)
            self.right_list_xlsx.setCurrentIndex(min(1, len(ids_con_ntc_vacio)-1))
        self.btn_continuar.setEnabled(True)


    
    
        