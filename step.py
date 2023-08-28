from nicegui import ui


class Step:
    def __init__(self, id, text, advance_fn=None, got_focus_fn=None):
        self.id = id
        self.text = text
        self.advance_fn = advance_fn
        self.got_focus_fn = got_focus_fn

    def to_ui(self):
        with ui.row().classes("items-center w-full max-w-screen-md"):
            self.id_label = ui.label(self.id).classes()
            self.label = ui.label(self.text).classes("grow")
            self.input = ui.label()
            self.compliance = ui.toggle(["Pass", "Fail"])

        self.compliance_prev = self.compliance.value
        self.compliance.on("click", lambda: self.reset_toggle_if_click_same(self.compliance.value))
        self.compliance.on("update:model-value", self.update_compliance_color)

    def reset_toggle_if_click_same(self, new_value):
        if new_value == self.compliance_prev:
            self.compliance.value = None

        self.compliance_prev = self.compliance.value

    async def focus(self):
        await ui.run_javascript(f"getElement({self.compliance.id}).$el.firstChild.focus()")

    def update_compliance_color(self, event=None):
        if self.compliance.value == "Pass":
            self.compliance.classes(add="toggle-pass", remove="toggle-fail")
            self.compliance.props("toggle-color=positive")
        elif self.compliance.value == "Fail":
            self.compliance.classes(add="toggle-fail", remove="toggle-pass")
            self.compliance.props("toggle-color=negative")
        else:
            self.compliance.classes(remove="toggle-pass toggle-fail")
            self.compliance.props("toggle-color=primary")


class ObservationStep(Step):
    def __init__(self, id, text, advance_fn=None, got_focus_fn=None):
        self.id = id
        self.text = text
        self.observe_fn = None
        self.spec = None
        self.validate_fn = None
        self.advance_fn = advance_fn
        self.got_focus_fn = got_focus_fn

    def capture(self, observe_fn):
        self.observe_fn = observe_fn
        return self

    def expect(self, spec):
        self.spec = spec
        self.validate_fn = spec.complies
        return self

    def to_ui(self):
        with ui.row().classes("items-center w-full max-w-screen-md"):
            self.id_label = ui.label(self.id).classes()
            self.label = ui.label(self.text).classes("grow")
            
            if self.spec:
                self.expect_label = ui.label(str(self.spec))

            if self.observe_fn:
                ui.button(icon="edit_note", on_click=self.observe)
            
            self.input = ui.input()
            self.compliance = ui.toggle(["Pass", "Fail"])

        self.compliance_prev = self.compliance.value
        self.compliance.on(
            "click",
            lambda: self.reset_toggle_if_click_same(self.compliance.value)
        )

        self.input.on("focusin", self.got_focus_fn)

        self.input.on("keypress", self.validate)
        self.compliance.on("update:model-value", self.update_compliance_color)

    def observe(self):
        measurement = self.observe_fn()
        self.input.set_value(measurement)
        self.input.run_method("focus")

    def focus(self):
        self.input.run_method("focus")

    async def validate(self, event):
        if event.args["keyCode"] != 13:
            return

        if self.validate_fn is None:
            await self.advance_fn()
            return
        
        self.compliance.set_value("Pass" if self.validate_fn(self.input.value) else "Fail")
        self.update_compliance_color()
        await self.advance_fn()