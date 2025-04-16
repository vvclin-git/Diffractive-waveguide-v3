import sys
import json
import os
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
    QMessageBox,
    QSizePolicy
)

CONFIG_PATH = '.\\configs'

# --- Updated widget for a grating element with additional fields ---
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QPushButton, QListWidget
from PySide6.QtCore import Qt

class GratingElementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initUI()
        
    
    def _initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        
        # --- Always visible header row ---
        headerLayout = QHBoxLayout()
        
        # Grating Name
        nameLabel = QLabel("Name:")
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Enter grating name")
        headerLayout.addWidget(nameLabel)
        headerLayout.addWidget(self.nameEdit)
        
        # Grating Pitch (Period) with unit "nm"
        pitchLabel = QLabel("Pitch:")
        self.pitchSpin = QDoubleSpinBox(self)
        self.pitchSpin.setRange(0.0, 10000.0)
        self.pitchSpin.setDecimals(3)
        self.pitchSpin.setSuffix(" nm")
        headerLayout.addWidget(pitchLabel)
        headerLayout.addWidget(self.pitchSpin)
        
        # Grating Vector: single spin box for the angle (–180° to 180°)
        vectorLabel = QLabel("Vector Angle:")
        self.vectorAngleSpin = QDoubleSpinBox(self)
        self.vectorAngleSpin.setRange(-180.0, 180.0)
        self.vectorAngleSpin.setDecimals(1)
        self.vectorAngleSpin.setSuffix(" °")
        headerLayout.addWidget(vectorLabel)
        headerLayout.addWidget(self.vectorAngleSpin)
        
        # Order field – text input for comma-delimited unique integers
        orderLabel = QLabel("Order:")
        self.orderEdit = QLineEdit(self)
        self.orderEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.orderEdit.setPlaceholderText("e.g. -1,0,1")
        headerLayout.addWidget(orderLabel)
        headerLayout.addWidget(self.orderEdit)
        
        mainLayout.addLayout(headerLayout)
        
        # --- Advanced row toggle button ---
        self.advancedButton = QPushButton("Show Advanced", self)
        self.advancedButton.setCheckable(True)
        self.advancedButton.setChecked(False)
        self.advancedButton.toggled.connect(self.toggleAdvanced)
        mainLayout.addWidget(self.advancedButton)
        
        # --- Advanced area arranged horizontally ---
        self.advancedArea = QWidget(self)
        advLayout = QHBoxLayout(self.advancedArea)
        advLayout.setContentsMargins(0, 0, 0, 0)
        
        # Mode: dropdown
        modeLabel = QLabel("Mode:")
        self.modeCombo = QComboBox(self)
        self.modeCombo.addItems(["All", "T&TIR"])
        advLayout.addWidget(modeLabel)
        advLayout.addWidget(self.modeCombo)
        
        # Pitch 2
        pitch2Label = QLabel("Pitch 2:")
        self.pitch2Spin = QDoubleSpinBox(self)
        self.pitch2Spin.setRange(0.0, 10000.0)
        self.pitch2Spin.setDecimals(3)
        self.pitch2Spin.setSuffix(" nm")
        advLayout.addWidget(pitch2Label)
        advLayout.addWidget(self.pitch2Spin)
        
        # Vector Angle 2
        vector2Label = QLabel("Vector Angle 2:")
        self.vectorAngle2Spin = QDoubleSpinBox(self)
        self.vectorAngle2Spin.setRange(-180.0, 180.0)
        self.vectorAngle2Spin.setDecimals(1)
        self.vectorAngle2Spin.setSuffix(" °")
        advLayout.addWidget(vector2Label)
        advLayout.addWidget(self.vectorAngle2Spin)
        
        # Order 2
        order2Label = QLabel("Order 2:")
        self.order2Edit = QLineEdit(self)
        self.order2Edit.setPlaceholderText("e.g. -1,0,1")
        self.orderEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        advLayout.addWidget(order2Label)
        advLayout.addWidget(self.order2Edit)
        
        self.advancedArea.setVisible(False)
        mainLayout.addWidget(self.advancedArea)
    
    def toggleAdvanced(self, checked):
        self.advancedArea.setVisible(checked)
        # Force advanced area and widget to recalc their sizes.
        self.advancedArea.adjustSize()
        self.adjustSize()
        self.updateGeometry()
        # If this widget is inside a QListWidget, update each item's size hint.
        listWidget = self._findParentListWidget()
        if listWidget:
            for i in range(listWidget.count()):
                item = listWidget.item(i)
                widget = listWidget.itemWidget(item)
                item.setSizeHint(widget.sizeHint())
            listWidget.doItemsLayout()
        self.advancedButton.setText("Hide Advanced" if checked else "Show Advanced")
    
    def _findParentListWidget(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, QListWidget):
                return parent
            parent = parent.parent()
        return None
    
    def getData(self):
        # Return a dictionary containing primary and advanced field values.
        return {
            "grating_name": self.nameEdit.text(),
            "pitch": self.pitchSpin.value(),
            "vector_angle": self.vectorAngleSpin.value(),
            "order": self.orderEdit.text(),
            "advanced": {
                "mode": self.modeCombo.currentText(),
                "pitch2": self.pitch2Spin.value(),
                "vector_angle2": self.vectorAngle2Spin.value(),
                "order2": self.order2Edit.text()
            }
        }
    
    def setData(self, data):
        self.nameEdit.setText(data.get("grating_name", ""))
        self.pitchSpin.setValue(data.get("pitch", 0))
        self.vectorAngleSpin.setValue(data.get("vector_angle", 0))
        self.orderEdit.setText(data.get("order", ""))
        adv = data.get("advanced", {})
        self.modeCombo.setCurrentText(adv.get("mode", "All"))
        self.pitch2Spin.setValue(adv.get("pitch2", 0))
        self.vectorAngle2Spin.setValue(adv.get("vector_angle2", 0))
        self.order2Edit.setText(adv.get("order2", ""))





# --- Grating Elements panel supporting drag, delete, and clear operations ---
class GratingElementsWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Grating Elements", parent)
        self._initUI()
    
    def _initUI(self):
        layout = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.listWidget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.listWidget)
        
        # Button row: Add, Delete, Clear
        btnLayout = QHBoxLayout()
        self.addButton = QPushButton("Add Grating", self)
        self.addButton.clicked.connect(self.addGrating)
        btnLayout.addWidget(self.addButton)
        
        self.deleteButton = QPushButton("Delete Grating", self)
        self.deleteButton.clicked.connect(self.deleteGrating)
        btnLayout.addWidget(self.deleteButton)
        
        self.clearButton = QPushButton("Clear Gratings", self)
        self.clearButton.clicked.connect(self.clearGratings)
        btnLayout.addWidget(self.clearButton)
        
        layout.addLayout(btnLayout)
    
    def addGrating(self):
        widget = GratingElementWidget(self)
        item = QListWidgetItem(self.listWidget)
        item.setSizeHint(widget.sizeHint())
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
    
    def deleteGrating(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            self.listWidget.takeItem(row)
        else:
            QMessageBox.information(self, "No Selection", "Please select a grating to delete.")
    
    def clearGratings(self):
        self.listWidget.clear()
    
    def getGratingElements(self):
        elements = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            widget = self.listWidget.itemWidget(item)
            elements.append(widget.getData())
        return elements
    
    def setGratingElements(self, elements):
        self.listWidget.clear()
        for element in elements:
            widget = GratingElementWidget(self)
            widget.setData(element)
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)

# --- Material Selection panel ---
class MaterialSelectionWidget(QGroupBox):
    def __init__(self, materials, parent=None):
        super().__init__("Material Selection", parent)
        self.materials = materials  # Loaded from materials.json
        self._initUI()

    def _initUI(self):
        layout = QFormLayout(self)
        self.ambientCombo = QComboBox(self)
        self.substrateCombo = QComboBox(self)
        for material in self.materials.keys():
            self.ambientCombo.addItem(material)
            self.substrateCombo.addItem(material)
        layout.addRow("Ambient Material:", self.ambientCombo)
        layout.addRow("Substrate Material:", self.substrateCombo)

    def getSelection(self):
        return {
            "ambient": self.ambientCombo.currentText(),
            "substrate": self.substrateCombo.currentText()
        }
    
    def setSelection(self, selection):
        ambient = selection.get("ambient", "")
        substrate = selection.get("substrate", "")
        index_a = self.ambientCombo.findText(ambient)
        if index_a != -1:
            self.ambientCombo.setCurrentIndex(index_a)
        index_s = self.substrateCombo.findText(substrate)
        if index_s != -1:
            self.substrateCombo.setCurrentIndex(index_s)

# --- System Parameters panel with updated FoV inputs ---
class SystemParametersWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("System Parameters", parent)
        self._initUI()

    def _initUI(self):
        layout = QFormLayout(self)
        # FoV: Two spin boxes for horizontal and vertical half-range (±)
        self.hFOV = QDoubleSpinBox(self)
        self.hFOV.setRange(0, 180)
        self.hFOV.setDecimals(1)
        self.hFOV.setSuffix(" °")
        self.vFOV = QDoubleSpinBox(self)
        self.vFOV.setRange(0, 180)
        self.vFOV.setDecimals(1)
        self.vFOV.setSuffix(" °")
        fovLayout = QHBoxLayout()
        fovLayout.addWidget(QLabel("Horizontal (±):"))
        fovLayout.addWidget(self.hFOV)
        fovLayout.addWidget(QLabel("Vertical (±):"))
        fovLayout.addWidget(self.vFOV)
        layout.addRow("Field of View (FoV):", fovLayout)

        # Eyebox size inputs (width and height in mm)
        self.eyeboxWidth = QDoubleSpinBox(self)
        self.eyeboxWidth.setRange(0, 1000)
        self.eyeboxWidth.setSuffix(" mm")
        self.eyeboxHeight = QDoubleSpinBox(self)
        self.eyeboxHeight.setRange(0, 1000)
        self.eyeboxHeight.setSuffix(" mm")
        whLayout = QHBoxLayout()
        whLayout.addWidget(QLabel("Width:"))
        whLayout.addWidget(self.eyeboxWidth)
        whLayout.addWidget(QLabel("Height:"))
        whLayout.addWidget(self.eyeboxHeight)
        layout.addRow("Eyebox Size:", whLayout)

        # Eye relief
        self.eyeRelief = QDoubleSpinBox(self)
        self.eyeRelief.setRange(0, 1000)
        self.eyeRelief.setSuffix(" mm")
        layout.addRow("Eye Relief:", self.eyeRelief)

        # Wavelength inputs for R, G, and B channels.
        self.wavelengthR = QDoubleSpinBox(self)
        self.wavelengthR.setRange(0, 10000)
        self.wavelengthR.setSuffix(" nm")
        self.wavelengthG = QDoubleSpinBox(self)
        self.wavelengthG.setRange(0, 10000)
        self.wavelengthG.setSuffix(" nm")
        self.wavelengthB = QDoubleSpinBox(self)
        self.wavelengthB.setRange(0, 10000)
        self.wavelengthB.setSuffix(" nm")
        wlLayout = QHBoxLayout()
        wlLayout.addWidget(QLabel("R:"))
        wlLayout.addWidget(self.wavelengthR)
        wlLayout.addWidget(QLabel("G:"))
        wlLayout.addWidget(self.wavelengthG)
        wlLayout.addWidget(QLabel("B:"))
        wlLayout.addWidget(self.wavelengthB)
        layout.addRow("Wavelength:", wlLayout)

    def getParameters(self):
        return {
            "fov": {
                "horizontal": self.hFOV.value(),
                "vertical": self.vFOV.value()
            },
            "eyebox": {
                "width": self.eyeboxWidth.value(),
                "height": self.eyeboxHeight.value()
            },
            "eye_relief": self.eyeRelief.value(),
            "wavelength": {
                "R": self.wavelengthR.value(),
                "G": self.wavelengthG.value(),
                "B": self.wavelengthB.value()
            }
        }
    
    def setParameters(self, params):
        fov = params.get("fov", {})
        self.hFOV.setValue(fov.get("horizontal", 0))
        self.vFOV.setValue(fov.get("vertical", 0))
        eyebox = params.get("eyebox", {})
        self.eyeboxWidth.setValue(eyebox.get("width", 0))
        self.eyeboxHeight.setValue(eyebox.get("height", 0))
        self.eyeRelief.setValue(params.get("eye_relief", 0))
        wavelength = params.get("wavelength", {})
        self.wavelengthR.setValue(wavelength.get("R", 0))
        self.wavelengthG.setValue(wavelength.get("G", 0))
        self.wavelengthB.setValue(wavelength.get("B", 0))

# --- Main Window that organizes all panels and configuration buttons ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optical Simulation UI")
        self._initUI()
        self.loadDefaultConfig()  # Attempt to load default.json on startup

    def _initUI(self):
        centralWidget = QWidget(self)
        mainLayout = QVBoxLayout(centralWidget)

        # Load materials from materials.json; use defaults if file not found.
        try:
            with open("materials.json", "r") as f:
                materials = json.load(f)
        except Exception as e:
            materials = {
                "Air": {"coefficient": [0, 0, 0, 0, 0, 0]},
                "LASF46B": {"coefficient": [2.17988922, 0.306495184, 1.56882437, 0.012580538, 0.056719137, 105.316538]}
            }

        self.materialSelection = MaterialSelectionWidget(materials, self)
        self.systemParams = SystemParametersWidget(self)
        self.gratingElements = GratingElementsWidget(self)

        mainLayout.addWidget(self.materialSelection)
        mainLayout.addWidget(self.systemParams)
        mainLayout.addWidget(self.gratingElements)

        # Button Panel for operations
        btnLayout = QHBoxLayout()
        self.printButton = QPushButton("Print Configuration", self)
        self.printButton.clicked.connect(self.printConfig)
        btnLayout.addWidget(self.printButton)

        self.loadConfigButton = QPushButton("Load Configuration", self)
        self.loadConfigButton.clicked.connect(self.loadConfiguration)
        btnLayout.addWidget(self.loadConfigButton)
        
        self.setDefaultButton = QPushButton("Set as Default", self)
        self.setDefaultButton.clicked.connect(self.setAsDefault)
        btnLayout.addWidget(self.setDefaultButton)

        self.saveAsButton = QPushButton("Save As", self)
        self.saveAsButton.clicked.connect(self.saveConfiguration)
        btnLayout.addWidget(self.saveAsButton)
        
        mainLayout.addLayout(btnLayout)

        self.setCentralWidget(centralWidget)
    
    def getCurrentConfig(self):
        return {
            "material_selection": self.materialSelection.getSelection(),
            "system_parameters": self.systemParams.getParameters(),
            "grating_elements": self.gratingElements.getGratingElements()
        }
    
    def applyConfiguration(self, config):
        if "material_selection" in config:
            self.materialSelection.setSelection(config["material_selection"])
        if "system_parameters" in config:
            self.systemParams.setParameters(config["system_parameters"])
        if "grating_elements" in config:
            self.gratingElements.setGratingElements(config["grating_elements"])
    
    def printConfig(self):
        config = self.getCurrentConfig()
        print(json.dumps(config, indent=4))
    
    def loadConfiguration(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    config = json.load(f)
                self.applyConfiguration(config)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration:\n{str(e)}")
    
    def saveConfiguration(self):
        config = self.getCurrentConfig()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration As", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=4)
                QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{str(e)}")
    
    def setAsDefault(self):
        config = self.getCurrentConfig()
        try:
            with open(f"{CONFIG_PATH}\\default.json", "w") as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, "Success", "Current configuration set as default.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save default configuration:\n{str(e)}")
    
    def loadDefaultConfig(self):
        if os.path.exists(f"{CONFIG_PATH}\\default.json"):
            try:
                with open(f"{CONFIG_PATH}\\default.json", "r") as f:
                    config = json.load(f)
                self.applyConfiguration(config)
            except Exception as e:
                QMessageBox.warning(self, "Default Config", f"Failed to load default.json:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec())
