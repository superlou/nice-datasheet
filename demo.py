from decimal import Decimal
from statistics import mean
from datetime import date, datetime
from sheet import Sheet
from specs import RangeSpec, DateSpec


def get_date():
    return date.today().strftime("%m/%d/%Y")


def get_steps_mean(steps):
    values = [float(step.input.value) for step in steps]
    return f"{mean(values):.3f}"


def build_filename(pn, sn):
    now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    return f"{pn.input.value}_{sn.input.value}_{now}.json"


s = Sheet("ATP 1234-1 Datasheet")
s.observe("", "Test operator")
s.observe("", "Test date", capture=get_date, spec=DateSpec())
pn = s.observe("", "EUT part number")
sn = s.observe("", "EUT serial number")
s.do("1.1", "Set POWER switch to ON")
s.observe("1.2", "Measure voltage of R1", unit="Ω", spec=RangeSpec("[5.50, 8.30]"))
s.observe("1.3", "Measure current of PSU", unit="V", spec=RangeSpec("[1, 2]"))

args = {
    "unit": "lb-in",
    "min_decimal_places": 2,
    "spec":RangeSpec("[0.50, 2.50]")
}
t1 = s.observe("1.4.1", "Measure the torque at the left-handed bolt harness.", **args)
t2 = s.observe("1.4.2", "Repeat step 1.4.1.", **args)
t3 = s.observe("1.4.2", "Repeat step 1.4.1.", **args)
s.observe(f"1.4.3", "Calculate the mean of the three torque measurements.", unit="lb-in",
          capture=lambda: get_steps_mean([t1, t2, t3]), spec=RangeSpec("[1.2, 1.8]"))

s.filename = lambda: build_filename(pn, sn)
s.run()
