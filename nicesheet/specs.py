import decimal
from decimal import Decimal
import re


class Spec:
    def __init__(self):
        pass

    def complies(self, text: str):
        raise NotImplementedError


class AnySpec(Spec):
    def complies(self, text: str):
        return text != ""

    def __str__(self):
        return "Any"


class RangeSpec(Spec):
    def __init__(self, range_str):
        self.range_str = range_str

        left, right = range_str.split(",")
        left = left.strip()
        right = right.strip()

        self.left_inclusive = left[0] == "["
        self.right_inclusive = right[-1] == "]"

        self.left_bound = Decimal(left[1:])
        self.right_bound = Decimal(right[:-1])

    def complies(self, text: str):
        try:
            value = Decimal(text)
        except (decimal.InvalidOperation, TypeError):
            return False

        left_bound = self.left_bound
        right_bound = self.right_bound

        left_ok = value >= left_bound if self.left_inclusive else value > left_bound
        right_ok = value <= right_bound if self.right_inclusive else value < right_bound
        return left_ok and right_ok

    def __str__(self):
        return self.range_str


class DateSpec(Spec):
    def __init__(self):
        pass

    def complies(self, text: str):
        pattern = r"\d{2}/\d{2}/\d{4}"
        return re.fullmatch(pattern, text)

    def __str__(self):
        return "mm/dd/yyyy"
    