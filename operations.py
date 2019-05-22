import unittest



def negative_decorator(function):
    def wrapper(number):
        if number < 0:
            sign = "-"
        else:
            sign = ""
        return int(sign + str(function(abs(number))))
    return wrapper


def class_with_value_decorator(cls):
    def increment_value_by(obj, extra):
        obj._value = obj._value + extra

    def _compute_name(obj):
        return obj._name.format(obj._value)

    cls.increment_value_by = increment_value_by
    cls._compute_name = _compute_name
    return cls


def reverse_as_str(number):
    return "".join(reversed(str(number)))


def add_digits(number, digits):
    return int(str(number) + str(digits))


@negative_decorator
def reverse(number):
    return int(reverse_as_str(number))


@negative_decorator
def mirror(number):
    return int("{}{}".format(number, reverse_as_str(number)))


def replace(value, old, new):
    return int(str(value).replace(str(old), str(new)))


def divideby(numerator, denominator):
    if numerator % denominator != 0:
        raise RuntimeError("Invalid int division")
    return numerator // denominator


@negative_decorator
def shift_left(value):
    number = str(value)
    if len(number) == 1:
        raise RuntimeError("Can only shift numbers with at least two digits")
    return int(number[:-1])


@negative_decorator
def circular_shift_right(number):
    number = str(number)
    return int(number[-1] + number[:-1])


@negative_decorator
def circular_shift_left(number):
    number = str(number)
    return int(number[1:] + number[0])


@negative_decorator
def sum_digits(number):
    return sum([int(i) for i in str(number)])


class Operation:
    def __init__(self, name, op):
        """
        Parameters
        ----------
        name : str
            The operation name
        op : callable
            A function performing the operation
        """
        self._name = name
        self._op = op

    @property
    def name(self):
        return self._name

    def apply(self, number):
        new_value = self._op(number)
        if new_value == number:
            raise RuntimeError("Useless operation")
        return new_value

    def _compute_name(self):
        return self._name

    def __repr__(self):
        return self._compute_name()


@class_with_value_decorator
class MultiplyX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("multiply by {}", lambda x: self._value * x)


@class_with_value_decorator
class DivideX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("divide by {}", lambda x: divideby(x, self._value))


@class_with_value_decorator
class SumX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("sum with {}", lambda x: self._value + x)


class Reverse(Operation):
    def __init__(self):
        super().__init__("reverse", reverse)


class Mirror(Operation):
    def __init__(self):
        super().__init__("mirror", mirror)


class Replace(Operation):
    def __init__(self, old, new):
        self._old = old
        self._new = new
        super().__init__(f"Replace {old} with {new}", lambda x: replace(x, old, new))


class CircularShiftRight(Operation):
    def __init__(self):
        super().__init__("shift right", circular_shift_right)


class CircularShiftLeft(Operation):
    def __init__(self):
        super().__init__("shift left", circular_shift_left)


class ShiftLeft(Operation):
    def __init__(self):
        super().__init__("<<", shift_left)

class SumDigits(Operation):
    def __init__(self):
        super().__init__("Sum", sum_digits)


class ModifyButtons_AddValue(Operation):
    def __init__(self, operations, value):
        self._operations = [i for i in operations if hasattr(i, "increment_value_by")]
        self._value = value
        super().__init__("[+]{}", self._modify_buttons)

    def _modify_buttons(self):
        for op in self._operations:
            op.increment_value_by(self._value)

    def _compute_name(self):
        return self._name.format(self._value)

    def apply(self, number):
        self._op()
        return number


@class_with_value_decorator
class AddDigits(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("Add digit {}", lambda x: add_digits(x, self._value))


class Tests(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse(123), 321)
        self.assertEqual(reverse(-123), -321)

    def test_mirror(self):
        self.assertEqual(mirror(123), 123321)
        self.assertEqual(mirror(-123), -123321)
        self.assertEqual(mirror(20), 2002)

    def test_op_class(self):
        r = Operation("reverse", reverse)
        self.assertEqual(r.apply(246), 642)
        self.assertEqual(r.name, "reverse")

    def test_replace(self):
        self.assertEqual(replace(-12345, 34, 99), -12995)
        self.assertEqual(replace(12345, 12, 00), 345)

    def test_divideby(self):
        self.assertEqual(divideby(15, 3), 5)
        self.assertEqual(divideby(-15, 3), -5)
        self.assertEqual(divideby(15, -3), -5)
        self.assertEqual(divideby(-15, -3), 5)
        with self.assertRaises(RuntimeError):
            divideby(10, 3)

    def test_circular_shift_right(self):
        self.assertEqual(circular_shift_right(351), 135)
        self.assertEqual(circular_shift_right(135), 513)
        self.assertEqual(circular_shift_right(-351), -135)
        self.assertEqual(circular_shift_right(500), 50)

    def test_circular_shift_left(self):
        self.assertEqual(circular_shift_left(351), 513)
        self.assertEqual(circular_shift_left(513), 135)
        self.assertEqual(circular_shift_left(-351), -513)
        self.assertEqual(circular_shift_left(500), 5)

    def test_shift_left(self):
        self.assertEqual(shift_left(351), 35)
        self.assertEqual(shift_left(135), 13)
        self.assertEqual(shift_left(-351), -35)

    def test_sum_digits(self):
        self.assertEqual(sum_digits(12345), 15)
        self.assertEqual(sum_digits(6677), 26)

    def test_add_digits(self):
        self.assertEqual(add_digits(123, 25), 12325)
        self.assertEqual(add_digits(0, 5), 5)
        self.assertEqual(add_digits(5, 0), 50)

    def test_ModifyButtons_AddValue(self):
        s = SumX(4)
        self.assertEqual(s._value, 4)
        self.assertEqual(s.apply(15), 19)

        m = ModifyButtons_AddValue([s], 9)
        m.apply(99999)
        self.assertEqual(s._value, 4+9)
        self.assertEqual(s.apply(20), 20+13)

# xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
if __name__ == "__main__":
    unittest.main()
