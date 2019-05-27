# pylint: disable=C0111
# pylint: disable=W0212

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


# @negative_decorator
def warp(number, enter_idx, exit_idx=0):
    factor = 10**exit_idx
    digits = str(number)
    warped_digits = digits[:-enter_idx]
    non_warped_digits = digits[-enter_idx:]
    out = int(non_warped_digits)
    for warped_digit in warped_digits:
        out = out + factor * int(warped_digit)

    # Reapply warp recursively until it does not change the result
    if out != number:
        out = warp(out, enter_idx, exit_idx)

    return out


@negative_decorator
def reverse(number):
    return int(reverse_as_str(number))


@negative_decorator
def mirror(number):
    if number > 999:
        raise ValueError("Too large")
    return int("{}{}".format(number, reverse_as_str(number)))


def replace(value, old, new):
    return int(str(value).replace(str(old), str(new)))


def divideby(numerator, denominator):
    if numerator % denominator != 0:
        raise ValueError("Invalid int division")
    return numerator // denominator


@negative_decorator
def shift_left(value):
    number = str(value)
    if len(number) == 1:
        raise ValueError("Can only shift numbers with at least two digits")
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


@negative_decorator
def inv10_each_digit(number):
    if number == 0:
        return 0

    if number < 10:
        # Number only has one digit
        return abs(10-number)

    digits = str(number)
    return "".join([str(inv10_each_digit(int(i))) for i in digits])


class Operation:
    def __init__(self, name):
        """
        Parameters
        ----------
        name : str
            The operation name
        op : callable
            A function performing the operation
        """
        self._name = name

    @property
    def name(self):
        return self._compute_name()

    def apply(self, number):
        new_value = self._apply_imp(number)
        if new_value == number:
            raise ValueError("Useless operation")
        return new_value

    def _apply_imp(self, number):
        raise NotImplementedError("Implement-me")

    def _compute_name(self):
        return self._name

    def __repr__(self):
        return self._compute_name()


@class_with_value_decorator
class MultiplyX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("multiply by {}")

    def _apply_imp(self, x):
        return self._value * x


@class_with_value_decorator
class DivideX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("divide by {}")

    def _apply_imp(self, x):
        return divideby(x, self._value)


@class_with_value_decorator
class SumX(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("sum with {}")

    def _apply_imp(self, x):
        return self._value + x


class Reverse(Operation):
    def __init__(self):
        super().__init__("reverse")

    def _apply_imp(self, number):
        return reverse(number)


class Mirror(Operation):
    def __init__(self):
        super().__init__("mirror")

    def _apply_imp(self, number):
        return mirror(number)


class Replace(Operation):
    def __init__(self, old, new):
        self._old = old
        self._new = new
        super().__init__(f"Replace {old} with {new}")

    def _apply_imp(self, x):
        return replace(x, self._old, self._new)


class CircularShiftRight(Operation):
    def __init__(self):
        super().__init__("shift right")

    def _apply_imp(self, value):
        return circular_shift_right(value)


class CircularShiftLeft(Operation):
    def __init__(self):
        super().__init__("shift left")

    def _apply_imp(self, number):
        return circular_shift_left(number)


class ShiftLeft(Operation):
    def __init__(self):
        super().__init__("<<")

    def _apply_imp(self, number):
        return shift_left(number)


class SumDigits(Operation):
    def __init__(self):
        super().__init__("Sum")

    def _apply_imp(self, number):
        return sum_digits(number)


class InvertSign(Operation):
    def __init__(self):
        super().__init__("+-")

    def _apply_imp(self, value):
        return -value


class ModifyButtons_AddValue(Operation):
    def __init__(self, operations, value):
        self._operations = [
            i for i in operations if hasattr(i, "increment_value_by")]
        self._value = value
        super().__init__("[+]{}")

    def _apply_imp(self, number):
        for op in self._operations:
            op.increment_value_by(self._value)

    def _compute_name(self):
        return self._name.format(self._value)

    def apply(self, number):
        self._apply_imp(number)
        return number


class StorageAction(Operation):
    def __init__(self):
        super().__init__("Store")


class RetrieveAction(Operation):
    def __init__(self):
        super().__init__("Retrieve")


@class_with_value_decorator
class AddDigits(Operation):
    def __init__(self, value):
        self._value = value
        super().__init__("Add digit {}")

    def _apply_imp(self, x):
        return add_digits(x, self._value)


class Inv10EachDigit(Operation):
    def __init__(self):
        super().__init__("Inv10")

    def _apply_imp(self, number):
        return inv10_each_digit(number)


class WarpAction(Operation):
    """
    Special action that can be added to a node and is automatically called
    after every action without decrementing the number of moves
    """
    def __init__(self, enter_idx, exit_idx):
        self._enter_idx = enter_idx
        self._exit_idx = exit_idx
        super().__init__("Warp")

    def apply(self, number):
        return warp(number, self._enter_idx, self._exit_idx)


class Tests(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse(123), 321)
        self.assertEqual(reverse(-123), -321)

    def test_mirror(self):
        self.assertEqual(mirror(123), 123321)
        self.assertEqual(mirror(-123), -123321)
        self.assertEqual(mirror(20), 2002)

    def test_replace(self):
        self.assertEqual(replace(-12345, 34, 99), -12995)
        self.assertEqual(replace(12345, 12, 00), 345)
        self.assertEqual(replace(2331, 31, "00"), 2300)

    def test_divideby(self):
        self.assertEqual(divideby(15, 3), 5)
        self.assertEqual(divideby(-15, 3), -5)
        self.assertEqual(divideby(15, -3), -5)
        self.assertEqual(divideby(-15, -3), 5)
        with self.assertRaises(ValueError):
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

    def test_inv10(self):
        self.assertEqual(inv10_each_digit(0), 0)
        self.assertEqual(inv10_each_digit(1), 9)
        self.assertEqual(inv10_each_digit(6), 4)
        self.assertEqual(inv10_each_digit(13), 97)
        self.assertEqual(inv10_each_digit(-13), -97)
        self.assertEqual(inv10_each_digit(30), 70)

    def test_warp(self):
        # Number in position 3 (1 in this case) is warped to position 0 and sum
        # with what is in position 0 (4 in this case)
        self.assertEqual(warp(1234, 3, 0), 235)
        self.assertEqual(warp(6123, 3, 0), 129)
        self.assertEqual(warp(991, 2, 0), 1)
        self.assertEqual(warp(255255, 3, 1), 375)

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
