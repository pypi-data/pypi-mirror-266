#  Copyright (c) 2020 - 2024 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Module for defining serialisers.

    The key component is the `SERIALISER_SPECS` mapping, which is based on
    the specification in `spec.clj`.
"""
from __future__ import annotations

from typing import Optional, TypeVar

from typing_extensions import Protocol

import typing

if typing.TYPE_CHECKING:
    from .base import Serialiser, Resolver
    from ..services import ServiceValue

T = TypeVar("T")


def get_serialiser(
    name: typing.Optional[str] = None, resolver: Optional[Resolver] = None
) -> Serialiser:
    from .spec import NULL_VALUE_KEY

    """ Retrieve a serialiser instance based on the spec name. """
    from .base import Serialiser

    return Serialiser.by_name(
        NULL_VALUE_KEY if name is None else name, resolver=resolver
    )


class Serialisable(Protocol):
    @classmethod
    def from_fields(cls: typing.Type[T], **kwargs) -> T:
        pass  # pragma: no cover

    @classmethod
    def from_service_value(
        cls: typing.Type[T], item: ServiceValue
    ) -> T:
        pass  # pragma: no cover


Serialisable_T = TypeVar(
    "Serialisable_T", bound=Serialisable
)
