from nicegui import ui
from step import SimpleStep, ObservationStep


class Sheet:
    def __init__(self, **kwargs):
        self.steps = []
        self.current_step = 0
        self.title = kwargs.get("title", None)

    def observe(self, id, text, **kwargs):
        index = len(self.steps)
        step = ObservationStep(id, text, {
            "advance": self.advance,
            "got_focus": lambda: self.got_focus(index)
        }, **kwargs)
        self.steps.append(step)
        return step
    
    def do(self, id, text):
        index = len(self.steps)
        step = SimpleStep(id, text, {
            "advance": self.advance,
            "got_focus": lambda: self.got_focus(index)
        })
        self.steps.append(step)
        return step
    
    def run(self):
        if self.title:
            ui.label(self.title).classes("text-h1")

        with ui.row().classes("max-w-screen-lg items-center fit row wrap q-px-md q-py-xs"):
            ui.label("Ref").classes("col-1 text-h6")
            ui.label("Description").classes("col text-h6")
            ui.label("Specification").classes("col-2 text-h6")
            ui.label("Data").classes("col-3 text-h6")
            ui.label("Result").classes("col-1 text-h6")


        self.current_step = 0

        for step in self.steps:
            step.to_ui()
    
        ui.run()
    
    async def advance(self):
        self.current_step += 1
        await self.steps[self.current_step].highlight()

    async def got_focus(self, index):
        self.current_step = index

        for step in self.steps:
            await step.dehighlight()

        await self.steps[self.current_step].highlight()        
