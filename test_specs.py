from decimal import Decimal
from specs import RangeSpec


def test_range_spec():
    s = RangeSpec("[1, 2.5]")
    assert str(s) == "[1, 2.5]"

    assert s.complies("0.99") ==False
    assert s.complies("1") == True
    assert s.complies("2.5") == True
    assert s.complies("2.51") == False

    s = RangeSpec("(1, 2.5)")
    assert str(s) == "(1, 2.5)"

    assert s.complies("0.99") == False
    assert s.complies("1") == False
    assert s.complies("1.01") == True
    assert s.complies("2.49") == True
    assert s.complies("2.50") == False
    assert s.complies("2.51") == False