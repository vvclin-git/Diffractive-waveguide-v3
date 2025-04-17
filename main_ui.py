
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QMessageBox
)
from widgets.main_window import MainWindow
from controller import *

import sys


app = QApplication(sys.argv)
window = MainWindow()
backend = BackendService(window.controller)



window.resize(600, 600)
window.show()
sys.exit(app.exec())