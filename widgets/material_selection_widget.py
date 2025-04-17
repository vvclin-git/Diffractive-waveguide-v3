from PySide6.QtWidgets import QGroupBox, QFormLayout, QComboBox

class MaterialSelectionWidget(QGroupBox):
    def __init__(self, materials, parent=None):
        super().__init__("Material Selection", parent)
        self.materials = materials
        self._initUI()

    def _initUI(self):
        layout = QFormLayout(self)
        self.ambientCombo = QComboBox(self)
        self.substrateCombo = QComboBox(self)
        for m in self.materials:
            self.ambientCombo.addItem(m)
            self.substrateCombo.addItem(m)
        layout.addRow("Ambient Material:", self.ambientCombo)
        layout.addRow("Substrate Material:", self.substrateCombo)

    def getSelection(self):
        return {
            "ambient": self.ambientCombo.currentText(),
            "substrate": self.substrateCombo.currentText()
        }

    def setSelection(self, sel):
        idx = self.ambientCombo.findText(sel.get("ambient", ""))
        if idx != -1:
            self.ambientCombo.setCurrentIndex(idx)
        idx = self.substrateCombo.findText(sel.get("substrate", ""))
        if idx != -1:
            self.substrateCombo.setCurrentIndex(idx)


# --- Test Section ---
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    materials = {"Air": {}, "LASF46B": {}}
    app = QApplication(sys.argv)
    w = MaterialSelectionWidget(materials)
    w.setWindowTitle("MaterialSelectionWidget Test")
    w.show()
    sys.exit(app.exec())
