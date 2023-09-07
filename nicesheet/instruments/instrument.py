from serial.tools import list_ports
from nicegui import ui, app


class Instrument:
    @property
    def model(self):
        raise NotImplementedError

    def to_ui(self):
        with ui.expansion() as expansion:
            self.config_expansion = expansion
            with expansion.add_slot("header"):
                with ui.row().classes('w-full max-w-screen-lg items-center'):
                    self.test_button = ui.button(icon="help_center")
                    self.test_button.on("click.stop", self.handle_test_connection)
                    ui.label(f"{self.name} ({self.device_model})")

            expansion.classes('w-full')
            self.test_button.props("flat")

            self.build_ui_options()

    def build_ui_options(self):
        raise NotImplementedError

    def handle_test_connection(self):
        result = self.test_connection()

        if isinstance(result, Exception):
            color = "negative"
            msg = "Connection failed!\n" + repr(result)
            self.config_expansion.run_method("show")
            icon = "link_off"
        else:
            color = "positive"
            msg = result
            self.config_expansion.run_method("hide")
            icon = "link"
        
        self.test_button.props(f"color={color} icon={icon}")
        ui.notify(msg, type=color, multi_line=True, classes="multi-line-notification")

    def test_connection(self):
        raise NotImplementedError

    def prep_storage(self):
        if "instruments" not in app.storage.general:
            app.storage.general["instruments"] = {}

        try:
            record = app.storage.general["instruments"][self.name]
        except KeyError:
            record = {}
            app.storage.general["instruments"][self.name] = record


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