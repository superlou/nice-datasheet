import json
from pathlib import Path
from datetime import datetime
from nicegui import ui
from step import SimpleStep, ObservationStep


class Sheet:
    def __init__(self, **kwargs):
        self.steps = []
        self.current_step = 0
        self.title = kwargs.get("title", None)

    def observe(self, ref, text, **kwargs):
        index = len(self.steps)
        step = ObservationStep(ref, text, {
            "advance": self.advance,
            "got_focus": lambda: self.got_focus(index),
            "changed": self.on_changed,
        }, **kwargs)
        self.steps.append(step)
        return step
    
    def do(self, ref, text):
        index = len(self.steps)
        step = SimpleStep(ref, text, {
            "advance": self.advance,
            "got_focus": lambda: self.got_focus(index),
            "changed": self.on_changed,
        })
        self.steps.append(step)
        return step
    
    def run(self):
        if self.title:
            ui.label(self.title).classes("text-h1")

        with ui.row().classes("max-w-screen-lg items-center fit row no-wrap"):
            ui.label("Ref").classes("col-1 text-h6")
            ui.label("Description").classes("col text-h6")
            ui.label("Specification").classes("col-2 text-h6")
            ui.label("Data").classes("col-3 text-h6")
            ui.label("Result").classes("col-1 text-h6")

        self.current_step = 0

        for step in self.steps:
            step.to_ui()
    
        with ui.row():
            ui.button("Print", icon="print", on_click=self.trigger_print_dialog)
            ui.button("Save Data", icon="save", on_click=self.download_json)

        ui.run()
    
    async def advance(self):
        self.current_step += 1
        await self.steps[self.current_step].highlight()

    async def got_focus(self, index):
        self.current_step = index

        for step in self.steps:
            await step.dehighlight()

        await self.steps[self.current_step].highlight()        

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


class SheetJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Sheet):
            return {
                "last-edit": datetime.now().isoformat(),
                "title": o.title,
                "steps": o.steps,
            }
        elif isinstance(o, SimpleStep):
            return {
                "ref": o.ref,
                "text": o.text,
                "compliance": o.compliance.value,
            }
        elif isinstance(o, ObservationStep):
            return {
                "ref": o.ref,
                "text": o.text,
                "input": o.input.value,
                "compliance": o.compliance.value,
            }
