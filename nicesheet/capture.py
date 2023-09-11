from statistics import mean
from datetime import date


def capture_def_parts(capture_def):
    capture_fn = None
    args = []
    kwargs = {}

    if isinstance(capture_def, tuple):
        capture_fn = capture_def[0]
        last_element = capture_def[-1]

        if isinstance(last_element, dict):
            args = capture_def[1:-1]
            kwargs = last_element
        else:
            args = capture_def[1:]
    else:
        capture_fn = capture_def

    return capture_fn, args, kwargs


def run_capture(capture_def):
    capture_fn, args, kwargs = capture_def_parts(capture_def)
    return capture_fn(*args, **kwargs)


async def run_async_capture(capture_def):
    capture_fn, args, kwargs = capture_def_parts(capture_def)
    return await capture_fn(*args, **kwargs)


def get_date():
    return date.today().strftime("%m/%d/%Y")


def get_steps_mean(steps):
    values = [float(step.input.value) for step in steps]
    return f"{mean(values):.3f}"
