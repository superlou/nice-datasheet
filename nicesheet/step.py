import traceback
from nicegui import ui
from asyncio import iscoroutinefunction
from .resettable_toggle import ResettableToggle
from .capture import capture_def_parts


class Step:
    def __init__(self, ref, text, emit):
        self.ref = ref
        self.text = text
        self.emit = emit
        self.row_classes = "max-w-screen-lg items-center fit row no-wrap highlight-focus"

    def to_ui(self):
        with ui.row().classes(self.row_classes) as row:
            self.row = row
            self.build_ui()
            with ui.row().classes("col-1"):
                self.compliance = ResettableToggle(
                    ["Pass", "Fail"],
                    on_change=self.on_compliance_change
                ).on("keydown", self.on_compliance_keydown)

        self.compliance.props("dense unelevated")
        self.compliance.style("print-color-adjust: exact;")

    def build_ui(self):
        raise NotImplementedError

    def reset(self):
        self.compliance.set_value(None)

    async def on_compliance_change(self, evt):
        self.update_compliance_color()
        self.emit["changed"]()
        await self.emit["got_focus"]()

        if self.compliance.value is not None:
            await self.emit["advance"]()

    def update_compliance_color(self, event=None):
        if self.compliance.value == "Pass":
            self.compliance.props("toggle-color=positive")
        elif self.compliance.value == "Fail":
            self.compliance.props("toggle-color=negative")
        else:
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

    async def take_cursor(self):
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
            self.input.props("outlined dense").classes("col-3")

            if self.min_decimal_places is not None:
                self.input.on("keyup", self.warn_decimal_places,
                              throttle=1, leading_events=False)

            with self.input.add_slot("prepend"):
                if self.observe_fn:
                    self.observe_button = ui.button(icon="auto_fix_high",
                                                    on_click=self.observe)
                    self.observe_button.props("flat dense").classes("print-hide")

            with self.input.add_slot('append'):
                ui.label(self.unit).style("font-size:12pt")

        self.input.on("focusin", self.emit["got_focus"])
        self.input.on("keypress", self.on_input_keypress)

    def reset(self):
        super().reset()
        self.input.value = ""

    async def observe(self):
        if self.observe_fn is None:
            ui.notify(
                "This step does not have an automatic observation function",
                type="warning"
            )
            return

        self.observe_button.props("loading")

        capture_fn, args, kwargs = capture_def_parts(self.observe_fn)

        try:
            if iscoroutinefunction(capture_fn):
                measurement = await capture_fn(*args, **kwargs)
            else:
                measurement = capture_fn(*args, **kwargs)
            
            self.input.set_value(measurement)
        except Exception as e:
            print(traceback.format_exc())
            ui.notify(
                "Automatic observation failed!\n" + str(e),
                type="negative",
                multi_line=True,
                classes='multi-line-notification',
            )
        
        self.observe_button.props(remove="loading")
        self.input.run_method("focus")

    def on_input_change(self):
        self.emit["changed"]()

    def warn_decimal_places(self):
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
        
        return warn

    async def take_cursor(self):
        self.input.run_method("focus")
    
    async def on_input_keypress(self, event):
        # On Chrome on Windows ctrl+enter uses keycode 10
        if event.args["keyCode"] in [13, 10] and event.args["ctrlKey"]:
            await self.observe()
            return

        if event.args["keyCode"] == 13 and event.args["shiftKey"]:
            await self.emit["go_back"]()
            return

        if event.args["keyCode"] == 13 and not event.args["ctrlKey"]:
            if self.min_decimal_places is not None and self.warn_decimal_places():
                # Don't advance if insufficient decimal places
                return

            if self.validate_fn is None:
                self.compliance.set_value("Pass")
                await self.emit["advance"]()
                return
            
            self.compliance.set_value("Pass" if self.validate_fn(self.input.value) else "Fail")
            await self.emit["advance"]()
