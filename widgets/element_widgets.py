from PySide6.QtCore import Qt, QEvent, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QDoubleSpinBox,
    QLabel, QComboBox, QPushButton, QListWidget, QListWidgetItem,
    QSizePolicy, QGroupBox, QMessageBox
)

class ElementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initUI()

    def _initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)

        headerLayout = QHBoxLayout()

        nameLabel = QLabel("Name:")
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText("Enter grating name")
        headerLayout.addWidget(nameLabel)
        headerLayout.addWidget(self.nameEdit)

        pitchLabel = QLabel("Pitch:")
        self.pitchSpin = QDoubleSpinBox(self)
        self.pitchSpin.setRange(0.0, 10000.0)
        self.pitchSpin.setDecimals(3)
        self.pitchSpin.setSuffix(" nm")
        headerLayout.addWidget(pitchLabel)
        headerLayout.addWidget(self.pitchSpin)

        vectorLabel = QLabel("Vector Angle:")
        self.vectorAngleSpin = QDoubleSpinBox(self)
        self.vectorAngleSpin.setRange(-180.0, 180.0)
        self.vectorAngleSpin.setDecimals(1)
        self.vectorAngleSpin.setSuffix(" °")
        headerLayout.addWidget(vectorLabel)
        headerLayout.addWidget(self.vectorAngleSpin)

        orderLabel = QLabel("Order:")
        self.orderEdit = QLineEdit(self)
        self.orderEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.orderEdit.setPlaceholderText("e.g. -1,0,1")
        headerLayout.addWidget(orderLabel)
        headerLayout.addWidget(self.orderEdit)

        mainLayout.addLayout(headerLayout)

        self.advancedButton = QPushButton("Show Advanced", self)
        self.advancedButton.setCheckable(True)
        self.advancedButton.toggled.connect(self.toggleAdvanced)
        mainLayout.addWidget(self.advancedButton)

        self.advancedArea = QWidget(self)
        advLayout = QHBoxLayout(self.advancedArea)
        advLayout.setContentsMargins(0, 0, 0, 0)

        modeLabel = QLabel("Mode:")
        self.modeCombo = QComboBox(self)
        self.modeCombo.addItems(["All", "T&TIR"])
        advLayout.addWidget(modeLabel)
        advLayout.addWidget(self.modeCombo)

        pitch2Label = QLabel("Pitch 2:")
        self.pitch2Spin = QDoubleSpinBox(self)
        self.pitch2Spin.setRange(0.0, 10000.0)
        self.pitch2Spin.setDecimals(3)
        self.pitch2Spin.setSuffix(" nm")
        advLayout.addWidget(pitch2Label)
        advLayout.addWidget(self.pitch2Spin)

        vector2Label = QLabel("Vector Angle 2:")
        self.vectorAngle2Spin = QDoubleSpinBox(self)
        self.vectorAngle2Spin.setRange(-180.0, 180.0)
        self.vectorAngle2Spin.setDecimals(1)
        self.vectorAngle2Spin.setSuffix(" °")
        advLayout.addWidget(vector2Label)
        advLayout.addWidget(self.vectorAngle2Spin)

        order2Label = QLabel("Order 2:")
        self.order2Edit = QLineEdit(self)
        self.order2Edit.setPlaceholderText("e.g. -1,0,1")
        self.order2Edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        advLayout.addWidget(order2Label)
        advLayout.addWidget(self.order2Edit)

        self.advancedArea.setVisible(False)
        mainLayout.addWidget(self.advancedArea)

    def toggleAdvanced(self, checked):
        self.advancedArea.setVisible(checked)
        self.advancedArea.adjustSize()
        self.adjustSize()
        self.updateGeometry()
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


class ElementsWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Grating Elements", parent)
        self._initUI()

    def _initUI(self):
        layout = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.listWidget.setDragDropMode(QListWidget.InternalMove)
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listWidget.viewport().installEventFilter(self)
        layout.addWidget(self.listWidget)

        btnLayout = QHBoxLayout()
        self.addButton = QPushButton("Add Element", self)
        self.addButton.clicked.connect(self.addElement)
        btnLayout.addWidget(self.addButton)

        self.deleteButton = QPushButton("Delete Element", self)
        self.deleteButton.clicked.connect(self.deleteElement)
        btnLayout.addWidget(self.deleteButton)

        self.clearButton = QPushButton("Clear Elements", self)
        self.clearButton.clicked.connect(self.clearElements)
        btnLayout.addWidget(self.clearButton)

        layout.addLayout(btnLayout)

    def addElement(self):
        widget = ElementWidget(self)
        item = QListWidgetItem(self.listWidget)
        item.setSizeHint(widget.sizeHint())
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        self._updateItemSizes()

    def deleteElement(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            self.listWidget.takeItem(row)
            self._updateItemSizes()
        else:
            QMessageBox.information(self, "No Selection", "Please select an element to delete.")

    def clearElements(self):
        self.listWidget.clear()
        self._updateItemSizes()

    def eventFilter(self, source, event):
        if source is self.listWidget.viewport() and event.type() == QEvent.Resize:
            self._updateItemSizes()
        return super().eventFilter(source, event)

    def _updateItemSizes(self):
        vw = self.listWidget.viewport().width()
        for i in range(self.listWidget.count()):
            itm = self.listWidget.item(i)
            wdg = self.listWidget.itemWidget(itm)
            if wdg:
                h = wdg.sizeHint().height()
                itm.setSizeHint(QSize(vw, h))
        self.listWidget.doItemsLayout()

    def getElements(self):
        return [
            self.listWidget.itemWidget(self.listWidget.item(i)).getData()
            for i in range(self.listWidget.count())
        ]

    def setElements(self, elements):
        self.listWidget.clear()
        for el in elements:
            widget = ElementWidget(self)
            widget.setData(el)
            item = QListWidgetItem(self.listWidget)
            item.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(item)
            self.listWidget.setItemWidget(item, widget)
        self._updateItemSizes()


# --- Test Section ---
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ElementsWidget()
    w.setWindowTitle("ElementsWidget Test")
    w.show()
    sys.exit(app.exec())
