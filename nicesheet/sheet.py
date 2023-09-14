import json
from pathlib import Path
from datetime import datetime
from nicegui import ui
from .step import SimpleStep, ObservationStep
from .system_info import get_system_info


package_directory = Path(__file__).parent


def extract_ref(text):
    if text[0] == "(":
        ref, procedure = text[1:].split(")")
        ref = ref.strip()
        procedure = procedure.strip()
        return ref, procedure
    else:
        return None, text


class Sheet:
    def __init__(self, title, version, **kwargs):
        self.steps = []
        self.current_step = 0
        self.instruments = []
        self.title = title
        self.version = version

    def observe(self, text, **kwargs):
        index = len(self.steps)
        ref, procedure = extract_ref(text)
        step = ObservationStep(ref, procedure, {
            "advance": self.on_advance,
            "go_back": self.on_go_back,
            "got_focus": lambda: self.focus_step(index),
            "changed": self.on_changed,
            "clicked": self.on_click_step,
        }, **kwargs)
        self.steps.append(step)
        return step
    
    def do(self, text):
        index = len(self.steps)
        ref, procedure = extract_ref(text)
        step = SimpleStep(ref, procedure, {
            "advance": self.on_advance,
            "go_back": self.on_go_back,
            "got_focus": lambda: self.focus_step(index),
            "changed": self.on_changed,
            "clicked": self.on_click_step,
        })
        self.steps.append(step)
        return step
    
    def instrument(self, instrument):
        self.instruments.append(instrument)

    def run(self):
        self.dark_mode = ui.dark_mode()
        self.add_note_requested = False
        ui.add_head_html("<style>"
                         + open(package_directory / "style.css").read()
                         + "</style>")

        with ui.header().props("reveal").classes("items-center"):
            with ui.row().classes("col items-baseline"):
                ui.label(self.title).classes("text-h6")
                ui.label(self.version)
            self.add_note().props("flat color=white dense").classes("print-hide")
            self.color_choice().props("flat color=white dense").classes("print-hide")
            ui.button("Print", icon="print", on_click=self.finish) \
                .props("flat color=white dense") \
                .classes("print-hide")
            ui.button("Reset", icon="delete", on_click=self.reset) \
                .props("flat color=white dense") \
                .classes("print-hide")

        for instrument in self.instruments:
            instrument.to_ui()

        with ui.row().classes("max-w-screen-lg items-center fit row no-wrap"):
            ui.label("Ref").classes("col-1 text-h6")
            ui.label("Procedure").classes("col text-h6")
            ui.label("Specification").classes("col-2 text-h6")
            ui.label("Observation").classes("col-3 text-h6")
            ui.label("Result").classes("col-1 text-h6")

        self.current_step = 0

        for step in self.steps:
            step.to_ui()
    
        with ui.row():
            ui.button("Print", icon="print", on_click=self.finish).classes("print-hide")

        self.system_info = get_system_info()

        ui.run(title=self.title, favicon=package_directory / "assets/favicon.ico")
    
    async def on_advance(self):
        self.current_step += 1
        await self.steps[self.current_step].take_cursor()

    async def on_go_back(self):
        self.current_step -= 1
        await self.steps[self.current_step].take_cursor()

    async def focus_step(self, index):
        self.current_step = index

    async def finish(self):
        filename = "data/" + self.filename()
        self.write_json(filename)
        await self.trigger_print_dialog()

    async def trigger_print_dialog(self):
        await ui.run_javascript("window.print();", respond=False)
    
    def on_changed(self):
        self.write_json()
    
    def write_json(self, filename=None):
        Path("data").mkdir(exist_ok=True)

        if filename is None:
            filename = "data/tmp.json"

        json.dump(self, open(filename, "w"), indent=4, cls=SheetJSONEncoder)

    def download_json(self):
        filename = "data/" + self.filename()
        self.write_json(filename)
        ui.download(filename)

    def add_note(self):
        self.add_note_button = ui.button("Add note", icon="edit_note", on_click=self.on_click_add_note)
        return self.add_note_button

    def on_click_add_note(self):
        if self.add_note_requested is False:
            self.add_note_requested = True
            self.add_note_button.set_text("Click step")
        else:
            self.add_note_requested = False
            self.add_note_button.set_text("Add note")

    def on_click_step(self, step):
        if self.add_note_requested:
            step.add_note()
            self.add_note_requested = False
            self.add_note_button.set_text("Add note")

    def color_choice(self):
        def toggle_dark_mode(button):
            if self.dark_mode.value is True:
                self.dark_mode.disable()
                button.props("icon=dark_mode")
                button.set_text("Dark Mode")
            else:
                self.dark_mode.enable()
                button.props("icon=light_mode")
                button.set_text("Light Mode")

        return ui.button(
            "Dark Mode",
            icon="light_mode" if self.dark_mode.value else "dark_mode",
            on_click=lambda evt: toggle_dark_mode(evt.sender)
        )

    def reset(self):
        for step in self.steps:
            step.reset()

class SheetJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Sheet):
            return {
                "last-edit": datetime.now().isoformat(),
                "title": o.title,
                "steps": o.steps,
                "system_info": o.system_info,
            }
        elif isinstance(o, SimpleStep):
            return {
                "ref": o.ref,
                "procedure": o.procedure,
                "compliance": o.compliance.value,
                "note": o.note,
            }
        elif isinstance(o, ObservationStep):
            return {
                "ref": o.ref,
                "procedure": o.procedure,
                "input": o.input.value,
                "compliance": o.compliance.value,
                "note": o.note,
            }
