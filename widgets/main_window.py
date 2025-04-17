import sys
import json
import os
from path import *
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
# from material_selection_widget import MaterialSelectionWidget
# from system_parameters_widget import SystemParametersWidget
# from element_widgets import ElementsWidget 

from .material_selection_widget import MaterialSelectionWidget
from .system_parameters_widget import SystemParametersWidget
from .element_widgets import ElementsWidget
from .ui_controller import UIController


# CONFIG_PATH = '.\\configs'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optical Simulation UI")
        self._initUI()
        self.loadDefaultConfig()
        self.controller = UIController(self)

    def _initUI(self):
        central = QWidget(self)
        mainLayout = QVBoxLayout(central)

        try:
            with open("materials.json", "r") as f:
                materials = json.load(f)
        except:
            materials = {"Air": {}, "LASF46B": {}}

        self.materialSelection = MaterialSelectionWidget(materials, self)
        self.systemParams = SystemParametersWidget(self)
        self.elements = ElementsWidget(self)

        mainLayout.addWidget(self.materialSelection)
        mainLayout.addWidget(self.systemParams)
        mainLayout.addWidget(self.elements)

        btnLayout = QHBoxLayout()
        for text, slot in [
            ("Print Configuration", self.printConfig),
            ("Load Configuration", self.loadConfiguration),
            ("Set as Default", self.setAsDefault),
            ("Save As", self.saveConfiguration)
        ]:
            btn = QPushButton(text, self)
            btn.clicked.connect(slot)
            btnLayout.addWidget(btn)
        mainLayout.addLayout(btnLayout)

        self.setCentralWidget(central)

    # def getCurrentConfig(self):
    #     return {
    #         "material_selection": self.materialSelection.getSelection(),
    #         "system_parameters": self.systemParams.getParameters(),
    #         "grating_elements": self.elements.getElements()  
    #     }

    def applyConfiguration(self, config):
        if "material_selection" in config:
            self.materialSelection.setSelection(config["material_selection"])
        if "system_parameters" in config:
            config["system_parameters"].setdefault(
                "show_rgb", {"R": True, "G": True, "B": True}
            )
            self.systemParams.setParameters(config["system_parameters"])
        if "grating_elements" in config:
            self.elements.setElements(config["grating_elements"])  

    # def printConfig(self):
    #     print(json.dumps(self.getCurrentConfig(), indent=4))
    
    def getCurrentConfig(self):
        dm = self.controller.update_model_from_ui()
        return dm


    def printConfig(self):
        dm = self.controller.update_model_from_ui()
        print(dm.to_dict())

    def loadConfiguration(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, "r") as f:
                    cfg = json.load(f)
                self.applyConfiguration(cfg)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def saveConfiguration(self):
        cfg = self.getCurrentConfig()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration As", "", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(cfg, f, indent=4)
                QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def setAsDefault(self):
        cfg = self.getCurrentConfig()
        os.makedirs(CONFIG_PATH, exist_ok=True)
        try:
            with open(f"{CONFIG_PATH}\\default.json", "w") as f:
                json.dump(cfg, f, indent=4)
            QMessageBox.information(self, "Success", "Set as default.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def loadDefaultConfig(self):
        path = f"{CONFIG_PATH}\\default.json"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    cfg = json.load(f)
                self.applyConfiguration(cfg)
            except Exception as e:
                QMessageBox.warning(self, "Default Config", str(e))


# --- Test Section ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 600)
    window.setWindowTitle("Optical Simulation UI Test")
    window.show()
    sys.exit(app.exec())
