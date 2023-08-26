from datetime import date
from sheet import Sheet


def get_date():
    return date.today().strftime("%m/%d/%Y")


def main():
    s = Sheet()
    s.observe("", "Test operator")
    s.observe("", "Test date", get_date)
    s.do("1.1", "Set POWER switch to ON")
    s.observe("1.2", "Measure voltage of R1", None, lambda x: float(x) > 5)
    s.observe("1.3", "Measure current of PSU")

    s.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()