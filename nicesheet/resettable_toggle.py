from nicegui import ui


class ResettableToggle(ui.toggle):
    def __init__(self, options, **kwargs):
        super().__init__(options, **kwargs)
        self.on("click", self.reset_if_click_same)
        self.prev_value = self.value

    def reset_if_click_same(self, evt):
        if self.value == self.prev_value:
            self.value = None

        self.prev_value = self.value