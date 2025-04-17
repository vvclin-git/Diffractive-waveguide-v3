# widgets/ui_controller.py
from PySide6.QtCore import QObject, Signal
from .data_model import (
    DataModel,
    MaterialSelectionModel,
    SystemParametersModel,
    GratingElementModel
)

class UIController(QObject):
    """
    Controller to sync between UI widgets and DataModel.
    Emits modelChanged whenever any field is updated.
    """
    modelChanged = Signal(DataModel)

    def __init__(self, main_window):
        super().__init__()
        self.win = main_window
        # Initialize model from current UI state
        self.model = self.update_model_from_ui()
        # Connect widget signals to handlers
        self._connect_signals()
    
    def update_model_from_ui(self):
        # read values from widgets
        ms = MaterialSelectionModel(**self.win.materialSelection.getSelection())
        sp = SystemParametersModel(**self.win.systemParams.getParameters())
        ge = [GratingElementModel(**e) for e in self.win.elements.getElements()]
        self.model = DataModel(ms, sp, ge)
        return self.model
    
    def _connect_signals(self):
        # MaterialSelection signals
        mat = self.win.materialSelection
        mat.ambientCombo.currentTextChanged.connect(self._on_ambient_changed)
        mat.substrateCombo.currentTextChanged.connect(self._on_substrate_changed)

        # SystemParameters signals
        sp = self.win.systemParams
        sp.hFOV.valueChanged.connect(self._on_hfov_changed)
        sp.vFOV.valueChanged.connect(self._on_vfov_changed)
        sp.eyeboxWidth.valueChanged.connect(self._on_eyewidth_changed)
        sp.eyeboxHeight.valueChanged.connect(self._on_eyeheight_changed)
        sp.eyeRelief.valueChanged.connect(self._on_eye_relief_changed)
        sp.wavelengthR.valueChanged.connect(self._on_wl_r_changed)
        sp.wavelengthG.valueChanged.connect(self._on_wl_g_changed)
        sp.wavelengthB.valueChanged.connect(self._on_wl_b_changed)
        sp.checkboxR.toggled.connect(self._on_show_r_changed)
        sp.checkboxG.toggled.connect(self._on_show_g_changed)
        sp.checkboxB.toggled.connect(self._on_show_b_changed)

        # ElementsWidget signals
        elems = self.win.elements
        lw = elems.listWidget
        for idx in range(lw.count()):
            item = lw.item(idx)
            w = lw.itemWidget(item)
            # Primary fields
            w.nameEdit.textChanged.connect(lambda txt, i=idx: self._on_elem_name_changed(i, txt))
            w.pitchSpin.valueChanged.connect(lambda v, i=idx: self._on_elem_pitch_changed(i, v))
            w.vectorAngleSpin.valueChanged.connect(lambda v, i=idx: self._on_elem_vector_changed(i, v))
            w.orderEdit.textChanged.connect(lambda txt, i=idx: self._on_elem_order_changed(i, txt))
            # Advanced toggle
            w.advancedButton.toggled.connect(lambda chk, i=idx: self._on_elem_adv_toggled(i, chk))
            # Advanced fields
            w.modeCombo.currentTextChanged.connect(lambda txt, i=idx: self._on_elem_mode_changed(i, txt))
            w.pitch2Spin.valueChanged.connect(lambda v, i=idx: self._on_elem_pitch2_changed(i, v))
            w.vectorAngle2Spin.valueChanged.connect(lambda v, i=idx: self._on_elem_vector2_changed(i, v))
            w.order2Edit.textChanged.connect(lambda txt, i=idx: self._on_elem_order2_changed(i, txt))

    # MaterialSelection handlers
    def _emit(self):
        self.modelChanged.emit(self.model)

    def _on_ambient_changed(self, text):
        self.model.material_selection.ambient = text; self._emit()

    def _on_substrate_changed(self, text):
        self.model.material_selection.substrate = text; self._emit()

    # SystemParameters handlers
    def _on_hfov_changed(self, v):
        self.model.system_parameters.fov['horizontal'] = v; self._emit()

    def _on_vfov_changed(self, v):
        self.model.system_parameters.fov['vertical'] = v; self._emit()

    def _on_eyewidth_changed(self, v):
        self.model.system_parameters.eyebox['width'] = v; self._emit()

    def _on_eyeheight_changed(self, v):
        self.model.system_parameters.eyebox['height'] = v; self._emit()

    def _on_eye_relief_changed(self, v):
        self.model.system_parameters.eye_relief = v; self._emit()

    def _on_wl_r_changed(self, v):
        self.model.system_parameters.wavelength['R'] = v; self._emit()

    def _on_wl_g_changed(self, v):
        self.model.system_parameters.wavelength['G'] = v; self._emit()

    def _on_wl_b_changed(self, v):
        self.model.system_parameters.wavelength['B'] = v; self._emit()

    def _on_show_r_changed(self, b):
        self.model.system_parameters.show_rgb['R'] = b; self._emit()

    def _on_show_g_changed(self, b):
        self.model.system_parameters.show_rgb['G'] = b; self._emit()

    def _on_show_b_changed(self, b):
        self.model.system_parameters.show_rgb['B'] = b; self._emit()

    # ElementWidget handlers
    def _on_elem_name_changed(self, idx, txt):
        self.model.grating_elements[idx].grating_name = txt; self._emit()

    def _on_elem_pitch_changed(self, idx, v):
        self.model.grating_elements[idx].pitch = v; self._emit()

    def _on_elem_vector_changed(self, idx, v):
        self.model.grating_elements[idx].vector_angle = v; self._emit()

    def _on_elem_order_changed(self, idx, txt):
        self.model.grating_elements[idx].order = txt; self._emit()

    def _on_elem_adv_toggled(self, idx, chk):
        # no state in model for toggle, only visibility
        self._emit()

    def _on_elem_mode_changed(self, idx, txt):
        self.model.grating_elements[idx].advanced['mode'] = txt; self._emit()

    def _on_elem_pitch2_changed(self, idx, v):
        self.model.grating_elements[idx].advanced['pitch2'] = v; self._emit()

    def _on_elem_vector2_changed(self, idx, v):
        self.model.grating_elements[idx].advanced['vector_angle2'] = v; self._emit()

    def _on_elem_order2_changed(self, idx, txt):
        self.model.grating_elements[idx].advanced['order2'] = txt; self._emit()
