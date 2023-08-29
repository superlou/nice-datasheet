from nicegui import ui


class Step:
    def __init__(self, id, text, emit):
        self.id = id
        self.text = text
        self.emit = emit
        self.row_classes = "items-center w-full max-w-screen-md q-px-md q-py-xs"

    def to_ui(self):
        with ui.row().classes(self.row_classes) as row:
            self.row = row
            self.build_ui()
            self.compliance = ui.toggle(["Pass", "Fail"])

        self.compliance.on("click", self.emit["got_focus"])

        self.compliance_prev = self.compliance.value
        self.compliance.on("click", lambda: self.reset_toggle_if_click_same(self.compliance.value))
        self.compliance.on("update:model-value", self.update_compliance_color)
        self.compliance.style("print-color-adjust: exact;")

    def build_ui(self):
        raise NotImplementedError

    def reset_toggle_if_click_same(self, new_value):
        if new_value == self.compliance_prev:
            self.compliance.value = None

        self.compliance_prev = self.compliance.value

    async def highlight(self):
        self.row.classes("shadow")

    async def dehighlight(self):
        self.row.classes(remove="shadow")

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


class SimpleStep(Step):
    def __init__(self, id, text, emit):
        super().__init__(id, text, emit)

    def build_ui(self):
        self.id_label = ui.label(self.id).classes()
        self.label = ui.label(self.text).classes("grow")
        self.input = ui.label()

    async def highlight(self):
        await super().highlight()
        await ui.run_javascript(f"getElement({self.compliance.id}).$el.firstChild.focus()")


class ObservationStep(Step):
    def __init__(self, id, text, emit):
        super().__init__(id, text, emit)
        self.id = id
        self.text = text
        self.observe_fn = None
        self.spec = None
        self.validate_fn = None
        self.emit = emit

    def capture(self, observe_fn):
        self.observe_fn = observe_fn
        return self

    def expect(self, spec):
        self.spec = spec
        self.validate_fn = spec.complies
        return self

    def build_ui(self):
        self.id_label = ui.label(self.id).classes()
        self.label = ui.label(self.text).classes("grow")
        
        if self.spec:
            self.expect_label = ui.label(str(self.spec))

        if self.observe_fn:
            ui.button(icon="edit_note", on_click=self.observe)
        
        self.input = ui.input()
        self.input.on("focusin", self.emit["got_focus"])
        self.input.on("keypress", self.validate)

    def observe(self):
        measurement = self.observe_fn()
        self.input.set_value(measurement)
        self.input.run_method("focus")

    async def highlight(self):
        await super().highlight()
        self.input.run_method("focus")
    
    async def validate(self, event):
        if event.args["keyCode"] != 13:
            return

        if self.validate_fn is None:
            await self.emit["advance"]()
            return
        
        self.compliance.set_value("Pass" if self.validate_fn(self.input.value) else "Fail")
        self.update_compliance_color()
        await self.emit["advance"]()