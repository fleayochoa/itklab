from PyQt6.QtWidgets import QApplication
import sys

from LVHV_UI.core.worker_threads import DataThread
from LVHV_UI.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # Crear thread que genera datos
    data_thread = DataThread()
    data_thread.new_data.connect(window.on_new_data)
    data_thread.finished.connect(window.on_data_finished)

    data_thread.start()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()