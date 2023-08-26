from nicegui import ui


class Step:
    def __init__(self, id, text):
        self.id = id
        self.text = text

    def to_ui(self):
        with ui.row().classes("items-center w-full max-w-screen-md"):
            self.id_label = ui.label(self.id).classes()
            self.label = ui.label(self.text).classes("grow")
            self.input = ui.label()
            self.step_result = ui.toggle(["Pass", "Fail"])

        self.step_result_prev = self.step_result
        self.step_result.on("click", lambda: self.reset_toggle_if_click_same(self.step_result.value))
        self.step_result.on("update:model-value", self.update_toggle_color)

    def reset_toggle_if_click_same(self, new_value):
        if new_value == self.step_result_prev:
            self.step_result.value = None

        self.step_result_prev = self.step_result.value

    def update_toggle_color(self, event=None):
        if self.step_result.value == "Pass":
            self.step_result.classes(add="toggle-pass", remove="toggle-fail")
            self.step_result.props("toggle-color=positive")
        elif self.step_result.value == "Fail":
            self.step_result.classes(add="toggle-fail", remove="toggle-pass")
            self.step_result.props("toggle-color=negative")
        else:
            self.step_result.classes(remove="toggle-pass toggle-fail")
            self.step_result.props("toggle-color=primary")


class ObservationStep(Step):
    def __init__(self, id, text, observe_fn=None, validate_fn=None):
        self.id = id
        self.text = text
        self.observe_fn = observe_fn
        self.validate_fn = validate_fn

    def to_ui(self):
        with ui.row().classes("items-center w-full max-w-screen-md"):
            self.id_label = ui.label(self.id).classes()
            self.label = ui.label(self.text).classes("grow")
            
            if self.observe_fn:
                ui.button(icon="edit_note", on_click=self.observe)
            
            self.input = ui.input()
            self.step_result = ui.toggle(["Pass", "Fail"])

        self.step_result_prev = self.step_result
        self.step_result.on("click", lambda: self.reset_toggle_if_click_same(self.step_result.value))

        self.input.on("keypress", self.validate)

    def observe(self):
        measurement = self.observe_fn()
        self.input.set_value(measurement)

    def validate(self, event):
        if event.args["keyCode"] != 13:
            return

        if self.validate_fn is None:
            return
        
        self.step_result.set_value("Pass" if self.validate_fn(self.input.value) else "Fail")
        self.update_toggle_color()