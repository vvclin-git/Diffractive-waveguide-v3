from PySide6.QtWidgets import (
    QGroupBox, QFormLayout, QHBoxLayout, QWidget,
    QLabel, QDoubleSpinBox, QCheckBox
)

class SystemParametersWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("System Parameters", parent)
        self._initUI()

    def _initUI(self):
        layout = QFormLayout(self)

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

        self.eyeRelief = QDoubleSpinBox(self)
        self.eyeRelief.setRange(0, 1000)
        self.eyeRelief.setSuffix(" mm")
        layout.addRow("Eye Relief:", self.eyeRelief)

        self.checkboxR = QCheckBox(self)
        self.checkboxG = QCheckBox(self)
        self.checkboxB = QCheckBox(self)
        self.wavelengthR = QDoubleSpinBox(self)
        self.wavelengthR.setRange(0, 10000)
        self.wavelengthR.setSuffix(" nm")
        self.wavelengthG = QDoubleSpinBox(self)
        self.wavelengthG.setRange(0, 10000)
        self.wavelengthG.setSuffix(" nm")
        self.wavelengthB = QDoubleSpinBox(self)
        self.wavelengthB.setRange(0, 10000)
        self.wavelengthB.setSuffix(" nm")

        wlContainer = QWidget(self)
        wlLayout = QHBoxLayout(wlContainer)
        wlLayout.setContentsMargins(0, 0, 0, 0)
        wlLayout.addWidget(self.checkboxR)
        wlLayout.addWidget(QLabel("R:"))
        wlLayout.addWidget(self.wavelengthR)
        wlLayout.addSpacing(10)
        wlLayout.addWidget(self.checkboxG)
        wlLayout.addWidget(QLabel("G:"))
        wlLayout.addWidget(self.wavelengthG)
        wlLayout.addSpacing(10)
        wlLayout.addWidget(self.checkboxB)
        wlLayout.addWidget(QLabel("B:"))
        wlLayout.addWidget(self.wavelengthB)
        layout.addRow("Wavelength:", wlContainer)

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
            },
            "show_rgb": {
                "R": self.checkboxR.isChecked(),
                "G": self.checkboxG.isChecked(),
                "B": self.checkboxB.isChecked()
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
        wl = params.get("wavelength", {})
        self.wavelengthR.setValue(wl.get("R", 0))
        self.wavelengthG.setValue(wl.get("G", 0))
        self.wavelengthB.setValue(wl.get("B", 0))
        rgb = params.get("show_rgb", {})
        self.checkboxR.setChecked(rgb.get("R", True))
        self.checkboxG.setChecked(rgb.get("G", True))
        self.checkboxB.setChecked(rgb.get("B", True))


# --- Test Section ---
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = SystemParametersWidget()
    w.setWindowTitle("SystemParametersWidget Test")
    w.show()
    sys.exit(app.exec())
