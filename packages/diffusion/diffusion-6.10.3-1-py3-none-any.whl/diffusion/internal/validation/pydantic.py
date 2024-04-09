#  Copyright (c) 2022 - 2024 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.
import typing

import diffusion.internal.pydantic_compat.v1 as pydantic
from typing_extensions import TypeAlias


class StrictPositiveIntClass(pydantic.StrictInt):
    """
    Strictly validated version of `int`.
    Accepts only `int` or any subclasses thereof. Must be positive.
    """
    ge = 1


class StrictNonNegativeIntClass(pydantic.StrictInt):
    """
    Strictly validated version of `int`.
    Accepts only `int` or any subclasses thereof. Must be non-negative.
    """
    ge = 0


class StrictNonNegativeFloatClass(pydantic.StrictFloat):
    """
    Strictly validated version of `float`.
    Accepts only `int` or any subclasses thereof. Must be non-negative.
    """
    ge = 0.0


if typing.TYPE_CHECKING:
    StrictPositiveInt = typing.Union[StrictPositiveIntClass, pydantic.StrictInt]
    """
    A positive `int`
    """
    StrictNonNegativeInt = typing.Union[StrictNonNegativeIntClass, pydantic.StrictInt]
    """
    A non-negative `int`
    """
    StrictNonNegativeFloat = typing.Union[StrictNonNegativeFloatClass, pydantic.StrictFloat]
    """
    A non-negative float
    """
else:
    StrictPositiveInt: TypeAlias = StrictPositiveIntClass
    """
    A positive `int`
    """
    StrictNonNegativeInt: TypeAlias = StrictNonNegativeIntClass
    """
    A non-negative `int`
    """
    StrictNonNegativeFloat: TypeAlias = StrictNonNegativeFloatClass
    """
    A non-negative float
    """

StrictNonNegative = typing.Union[StrictNonNegativeInt, StrictNonNegativeFloat]
"""
A non-negative `int` or `float`
"""
