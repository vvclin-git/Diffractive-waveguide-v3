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
from widgets import *
from control import *



app = QApplication(sys.argv)
window = MainWindow()

controller = AppController()




window.resize(600, 600)
window.show()
sys.exit(app.exec())