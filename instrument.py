from serial.tools import list_ports
from nicegui import ui


class Instrument:
    @property
    def model(self):
        raise NotImplementedError

    def to_ui(self):
        with ui.expansion() as expansion:
            with expansion.add_slot("header"):
                with ui.row().classes('w-full items-center'):
                    ui.label(f"{self.name} ({self.device_model})")
                    self.test_button = ui.button("Test", on_click=self.handle_test_connection)
            
            expansion.classes('w-full')
            expansion.props("expand-icon-toggle switch-toggle-side")
            self.build_ui_options()

    def build_ui_options(self):
        raise NotImplementedError

    def handle_test_connection(self):
        result = self.test_connection()

        if isinstance(result, Exception):
            color = "negative"
            msg = "Connection failed!\n" + repr(result)
        else:
            color = "positive"
            msg = result
        
        self.test_button.props(f"color={color}")
        ui.notify(msg, type=color, multi_line=True, classes="multi-line-notification")


    def test_connection(self):
        raise NotImplementedError


class InstrumentException(Exception):
    pass


class NoResponse(Exception):
    pass


class PortSelector(ui.select):
    def __init__(self, **kwargs):
        ports = list_ports.comports()
        ports_map = {p.device: f"{p.device}: {p.description}" for p in ports}
        super().__init__(ports_map, value=ports[0].device, **kwargs)
        self.on("click", self.update_options)
    
    def update_options(self):
        ports = list_ports.comports()
        ports_map = {p.device: f"{p.device}: {p.description}" for p in ports}
        self.set_options(ports_map)