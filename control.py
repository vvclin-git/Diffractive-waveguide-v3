class AppController:
    def __init__(self, backend, ui):
        self.backend = backend
        self.ui = ui
        self.setup_connections()

    def setup_connections(self):
        self.ui.on_user_input(self.handle_input)
        self.backend.on_data_ready(self.update_ui)

    def handle_input(self, input_data):
        self.backend.run_calculation(input_data)

    def update_ui(self, result):
        self.ui.display_result(result)
