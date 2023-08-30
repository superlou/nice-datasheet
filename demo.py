from datetime import date
from sheet import Sheet
from specs import RangeSpec, DateSpec


def get_date():
    return date.today().strftime("%m/%d/%Y")


s = Sheet()
s.observe("", "Test operator")
s.observe("", "Test date", capture=get_date, spec=DateSpec())
s.observe("", "EUT part number")
s.observe("", "EUT serial number")
s.do("1.1", "Set POWER switch to ON")
s.observe("1.2", "Measure voltage of R1", unit="Ω", spec=RangeSpec("[5.50, 8.30]"))
s.observe("1.3", "Measure current of PSU", unit="V", spec=RangeSpec("[1, 2]"))

s.run()
