from nicegui import ui
from step import Step, ObservationStep


class Sheet:
    def __init__(self):
        self.steps = []
        self.current_step = 0

    def observe(self, id, text):
        index = len(self.steps)
        step = ObservationStep(
            id, text,
            self.advance,
            lambda: self.got_focus(index)
        )
        self.steps.append(step)
        return step
    
    def do(self, id, text):
        index = len(self.steps)
        step = Step(
            id, text,
            self.advance, 
            lambda: self.got_focus(index)
        )
        self.steps.append(step)
        return step
    
    def run(self):
        self.current_step = 0

        for step in self.steps:
            step.to_ui()
    
        ui.run()
    
    async def advance(self):
        self.current_step += 1
        await self.steps[self.current_step].focus()

    def got_focus(self, index):
        self.current_step = index
