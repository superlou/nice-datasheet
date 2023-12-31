from datetime import datetime
from nicesheet import Sheet
from nicesheet.specs import AnySpec, RangeSpec, DateSpec
from nicesheet.capture import get_date, get_steps_mean
from nicesheet.instruments import BK5492


def build_filename(pn, sn):
    now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    return f"{pn.input.value}_{sn.input.value}_{now}.json"


meter = BK5492("DMM1")

s = Sheet("ATP 1234-1 Datasheet", "v1")
s.instrument(meter)
s.observe("Test operator", spec=AnySpec())
s.observe("Test date", capture=get_date, spec=DateSpec())
pn = s.observe("EUT part number")
sn = s.observe("EUT serial number")
s.do("(1.1) Set POWER switch to ON")
s.observe("(1.2) Measure resistance of R1", unit="Ω", spec=RangeSpec("[5.50, 8.30]"))
s.observe(
    "(1.3.1) Measure voltage across R1. **Do not** brush probe contacts across components.",
    capture=meter.measure_mvdc,
    unit="mV",
    spec=RangeSpec("[0, 2]")
)
s.observe(
    "(1.3.1) Measure AC voltage across R1",
    capture=meter.measure_mvac,
    unit="mV",
    spec=RangeSpec("[1, 2]")
)

args = {
    "unit": "lb-in",
    "min_decimal_places": 2,
    "spec":RangeSpec("[0.50, 2.50]")
}
t1 = s.observe("(1.4.1) Measure the torque at the left-handed bolt harness.", **args)
t2 = s.observe("(1.4.2) Repeat step 1.4.1.", **args)
t3 = s.observe("(1.4.3) Repeat step 1.4.1.", **args)
s.observe("(1.4.4) Calculate the mean of the three torque measurements.",
          capture=(get_steps_mean, [t1, t2, t3]),
          unit="lb-in",
          spec=RangeSpec("[1.2, 1.8]"))

s.filename = lambda: build_filename(pn, sn)
s.run()
