from nicegui import ui


class Step:
    def __init__(self, id, text, emit):
        self.id = id
        self.text = text
        self.emit = emit
        self.row_classes = "max-w-screen-lg items-center fit row wrap q-px-md q-py-xs"

    def to_ui(self):
        with ui.row().classes(self.row_classes) as row:
            self.row = row
            self.build_ui()
            with ui.row().classes("col-2"):
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
        self.id_label = ui.label(self.id).classes("col-1")
        self.label = ui.label(self.text).classes("col-grow")
        self.input = ui.label()

    async def highlight(self):
        await super().highlight()
        await ui.run_javascript(f"getElement({self.compliance.id}).$el.firstChild.focus()")


class ObservationStep(Step):
    def __init__(self, id, text, emit, **kwargs):
        super().__init__(id, text, emit)
        self.id = id
        self.text = text
        self.spec = None
        self.validate_fn = None
        self.emit = emit

        self.unit = kwargs.get("unit", None)
        self.observe_fn = kwargs.get("capture", None)
        self.spec = kwargs.get("spec", None)
        if self.spec is not None:
            self.validate_fn = self.spec.complies

    def build_ui(self):
        self.id_label = ui.label(self.id).classes("col-1")
        self.text = ui.label(self.text).classes("col-grow")
        
        self.expect_label = ui.label(str(self.spec)).classes("col-2")
        
        with ui.input().classes("col-2") as input_field:
            self.input = input_field
            self.input.props("outlined")

            with input_field.add_slot('prepend'):
                if self.observe_fn:
                    ui.button(icon="edit_note", on_click=self.observe) \
                        .props("flat dense")

            with input_field.add_slot('append'):
                ui.label(self.unit) 

        self.input.on("focusin", self.emit["got_focus"])
        self.input.on("keypress", self.on_input_keypress)

    def observe(self):
        if self.observe_fn is None:
            ui.notify(
                "This step does not have an automatic observation function",
                type="warning"
            )

        measurement = self.observe_fn()
        self.input.set_value(measurement)
        self.input.run_method("focus")

    async def highlight(self):
        await super().highlight()
        self.input.run_method("focus")
    
    async def on_input_keypress(self, event):
        if event.args["keyCode"] == 13 and event.args["ctrlKey"]:
            self.observe()

        if event.args["keyCode"] == 13 and not event.args["ctrlKey"]:
            if self.validate_fn is None:
                await self.emit["advance"]()
                return
            
            self.compliance.set_value("Pass" if self.validate_fn(self.input.value) else "Fail")
            self.update_compliance_color()
            await self.emit["advance"]()