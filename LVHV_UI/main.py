from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
import sys

from LVHV_UI.core.worker_threads import DataThread
from LVHV_UI.core.HV_source import HVSource
from LVHV_UI.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # Crear thread que genera datos
    data_thread = DataThread()
    data_thread.new_data.connect(window.on_new_data)
    # Crear thread que controla la fuente HV
    hv_thread = HVSource()

    window.start.connect(data_thread.data_start)
    hv_thread.progress.connect(window.HV_status_update)
    window.set_serial_params.connect(hv_thread.set_serial_params)
    window.set_source_params.connect(hv_thread.set_source_params)
    window.apply_params.connect(hv_thread.set_ready_to_send)
    window.close_signal.connect(hv_thread.quit)
    window.close_signal.connect(data_thread.close)

    data_thread.start()
    hv_thread.start()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()