import calculator

def test_add():
    assert calculator.add(2, 3) == 5
    assert calculator.add(-1, 1) == 0
    assert calculator.add(0, 0) == 0

def test_subtract():
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(0, 5) == -5
    assert calculator.subtract(-3, -2) == -1

def test_multiply():
    assert calculator.multiply(2, 3) == 6
    assert calculator.multiply(-2, 3) == -6
    assert calculator.multiply(0, 100) == 0
