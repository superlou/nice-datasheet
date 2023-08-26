from nicegui import ui
from step import Step, ObservationStep


class Sheet:
    def __init__(self):
        self.steps = []

    def observe(self, id, text, observe_fn=None, validate_fn=None):
        step = ObservationStep(id, text, observe_fn, validate_fn)
        self.steps.append(step)
    
    def do(self, id, text):
        step = Step(id, text)
        self.steps.append(step)
    
    def run(self):
        for step in self.steps:
            step.to_ui()
    
        ui.run()