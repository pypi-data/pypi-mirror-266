#
# exceptions.py - DeGirum Python SDK: exceptions
# Copyright DeGirum Corp. 2022
#
# Defines declarations of exceptions used by DeGirum Python SDK
#


class DegirumException(Exception):
    """
    Base type for all DeGirum exceptions.
    """


def validate_color_tuple(color) -> tuple:
    """Validate if color has acceptable representation.

    Args:
        color (Any): Color object to validate.

    Raises:
        DegirumException: if color is not a three-element tuple and each element is integer number.
    Returns:
        color sequence converted to tuple.
    """
    from collections.abc import Iterable, Sized

    if not isinstance(color, Iterable) or not isinstance(color, Sized):
        raise DegirumException(f"Given color '{color}' is not an iterable object")
    if len(color) != 3:
        raise DegirumException(
            f"Given color '{color}' must have exactly three elements"
        )
    ret = tuple(color)
    for e in color:
        if not isinstance(e, int):
            raise DegirumException(f"Given color '{color}' must have integer elements")
    return ret
