from system import *
import json
from path import *
from PySide6.QtCore import QObject, Slot
from widgets.data_model import DataModel

with open(f'{CONFIG_PATH}\\materials.json', 'r') as f:
    materials = json.load(f)


class K_dom_Controller:
    def __init__(self, dm):
        self.update(dm)
        self.k_dom.report()
    def update(self, dm):
        sub_material = dm.material_selection.substrate
        ambient_material = dm.material_selection.ambient
        hfov = dm.system_parameters.fov['horizontal']
        vfov = dm.system_parameters.fov['vertical'] 
        wavelength = dm.system_parameters.wavelength
        wavelength_chk = dm.system_parameters.show_rgb
        fov = [-0.5 * hfov, 0.5 * hfov, -0.5 * vfov, 0.5 * vfov]
        wv_list = [wavelength[k] / 1000 for k in wavelength if wavelength_chk[k]]
        self.k_dom = K_domain(Material(sub_material, materials[sub_material]['coefficient']), Material(ambient_material, materials[ambient_material]['coefficient']))
        self.k_dom.set_source(options = {'fov':fov, 'wavelength_list':wv_list, 'fov_grid':(5,5)})
        sequence = []
        for i, g in enumerate(dm.grating_elements):
            self.k_dom.add_element(Grating, {'name': g.grating_name, 'periods': [[g.pitch / 1000,g.vector_angle]]})
            order = [int(x) for x in g.order.split(',')]
            order.sort(reverse=True)
            sequence.append([i + 1, order[0:2]])
        self.k_dom.add_sequence(sequence)
        return

# backend.py



class BackendService(QObject):
    def __init__(self, ui_controller):
        super().__init__()
        self.ui_controller = ui_controller

        # 連接訊號到槽函式
        self.ui_controller.modelChanged.connect(self.on_model_changed)
        self.k_dom = K_dom_Controller(self.ui_controller.model)



    @Slot(DataModel)
    def on_model_changed(self, model: DataModel):
        """
        每次模型更新時呼叫。你可以在這裡觸發計算、
        存檔、網路請求或其他後端工作。
        """
        self.k_dom.update(model)
        self.k_dom.k_dom.report()
        self.k_dom.k_dom.tracing()
        self.k_dom.k_dom.draw()
        # data = model.to_dict()
        # # 範例：印出修改後的 substrate
        # substrate = model.material_selection.substrate
        # print(f"[Backend] New substrate: {substrate}")

        # # 範例：若 eye_relief 超過某個門檻，就做特別處理
        # if model.system_parameters.eye_relief > 50:
        #     self.handle_large_eye_relief(model.system_parameters.eye_relief)

    def handle_large_eye_relief(self, relief_value):
        # 這裡放任何你需要的後端處理邏輯
        print(f"[Backend] Eye relief too large: {relief_value} mm – taking action.")

# class AppController:
#     def __init__(self, backend, ui):
#         self.backend = backend
#         self.ui = ui
#         self.dm = ui.getCurrentConfig()
#         self.k_dom = K_dom_Controller(self.dm)
        # self.setup_connections()

    # def setup_connections(self):
    #     self.ui.on_user_input(self.handle_input)
    #     self.backend.on_data_ready(self.update_ui)

    # def handle_input(self, input_data):
    #     self.backend.run_calculation(input_data)

    # def update_ui(self, result):
    #     self.ui.display_result(result)
