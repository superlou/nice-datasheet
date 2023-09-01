from nicegui import ui


class Step:
    def __init__(self, ref, text, emit):
        self.ref = ref
        self.text = text
        self.emit = emit
        self.row_classes = "max-w-screen-lg items-center fit row no-wrap"

    def to_ui(self):
        with ui.row().classes(self.row_classes) as row:
            self.row = row
            self.build_ui()
            with ui.row().classes("col-1"):
                self.compliance = ui.toggle(["Pass", "Fail"])
                self.compliance.props("dense").style("height:56px")

        self.compliance.style("background:#f8f8f8")
        self.compliance.on("click", self.emit["got_focus"])
        self.compliance.props("unelevated")

        self.compliance_prev = self.compliance.value
        self.compliance.on("click", lambda: self.reset_toggle_if_click_same(self.compliance.value))
        self.compliance.on("update:model-value", self.update_compliance_color)
        # Can't use update:model-value for changed because clearing does not update model
        self.compliance.on("click", self.emit["changed"])
        self.compliance.on("keydown", self.on_compliance_keydown)

        self.compliance.style("print-color-adjust: exact;")

    def build_ui(self):
        raise NotImplementedError

    def reset_toggle_if_click_same(self, new_value):
        if new_value == self.compliance_prev:
            self.compliance.value = None

        self.compliance_prev = self.compliance.value

    async def highlight(self):
        self.row.style("background:#f2f7ff")

    async def dehighlight(self):
        self.row.style("background:auto")

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

    async def on_compliance_keydown(self, event):
        if event.args["keyCode"] == 37:
            await ui.run_javascript(
                f"getElement({self.compliance.id}).$el.firstChild.focus()",
                respond=False
            )
        elif event.args["keyCode"] == 39:
            await ui.run_javascript(
                f"getElement({self.compliance.id}).$el.lastChild.focus()",
                respond=False
            )


class SimpleStep(Step):
    def __init__(self, ref, text, emit):
        super().__init__(ref, text, emit)

    def build_ui(self):
        self.ref_label = ui.label(self.ref).classes("col-1")
        self.label = ui.label(self.text).classes("col")
        self.input = ui.label().classes("col-3")

    async def highlight(self):
        await super().highlight()
        await ui.run_javascript(
            f"getElement({self.compliance.id}).$el.firstChild.focus()",
            respond=False
        )


class ObservationStep(Step):
    def __init__(self, ref, text, emit, **kwargs):
        super().__init__(ref, text, emit)
        self.unit = kwargs.get("unit", None)
        self.observe_fn = kwargs.get("capture", None)
        self.spec = kwargs.get("spec", None)
        if self.spec is not None:
            self.validate_fn = self.spec.complies
        else:
            self.validate_fn = None
        self.min_decimal_places = kwargs.get("min_decimal_places", None)

    def build_ui(self):
        self.ref_label = ui.label(self.ref).classes("col-1")
        self.text = ui.label(self.text).classes("col")
        
        self.expect_label = ui.label(str(self.spec)).classes("col-2")
        
        with ui.input(on_change=self.on_input_change) as input_field:
            self.input = input_field
            self.input.props("outlined bg-color=white").classes("col-3")

            if self.min_decimal_places is not None:
                self.input.on("keydown", self.check_decimal_places)

            with self.input.add_slot("prepend"):
                if self.observe_fn:
                    ui.button(icon="auto_fix_high", on_click=self.observe) \
                        .props("flat dense").classes("print-hide")

            with self.input.add_slot('append'):
                ui.label(self.unit).style("font-size:12pt")

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

    def on_input_change(self):
        self.emit["changed"]()

        if self.min_decimal_places is not None:
            self.check_decimal_places()

    def check_decimal_places(self):
        parts = self.input.value.split(".")

        if self.input.value == "":
            warn = False
        elif len(parts) < 2:
            warn = True
        elif len(parts[1]) < self.min_decimal_places:
            warn = True
        else:
            warn = False

        if warn:
            self.input.props("color=negative bottom-slots")
            with self.input.add_slot("hint"):
                ui.label(f"{self.min_decimal_places} or more decimal places required!")
        else:
            self.input.props(remove="color=negative bottom-slots")

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
