#  Copyright (c) 2020 - 2024 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Serialisers for values consisting of multiple individual values. """

from __future__ import annotations

import dataclasses
import io
import typing
from typing import (
    Optional,
    cast,
    Collection,
    Dict,
    Generic,
    Iterable,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from stringcase import pascalcase

from diffusion.internal.encoded_data import EncodingProtocol, EncodingType, Int32
from diffusion.internal.encoded_data.exceptions import (
    DataValidationError,
    StreamExhausted,
)

if typing.TYPE_CHECKING:
    from .base import Resolver, resolve

from ..encoded_data.abstract import EncodingTypeVar, Enc_K, Enc_V, EncodingProtocolVar

T = TypeVar("T", bound=EncodingType)


class GenericScalarSetSerialiser(
    Generic[T, EncodingTypeVar], EncodingProtocol[typing.Type[EncodingTypeVar]]
):
    """Generic set for multiple scalar values.

    Not technically a set, more of a collection.
    """

    scalar_type: Type[T]

    def __init__(self, values: Collection[T]):
        self.values: Sequence[EncodingType] = [
            value if isinstance(value, EncodingType) else self.scalar_type(value)
            for value in values
        ]
        self.validate()

    @property
    def value(self):
        """ All the values; needed for compatibility with `EncodingType`. """
        return self.values

    @classmethod
    def read(cls, stream: io.BytesIO) -> GenericScalarSetSerialiser:
        """ Read the values from a stream. """
        result = []
        length = Int32.read(stream).value
        if length:
            while True:
                try:
                    result.append(cls.scalar_type.read(stream))
                except StreamExhausted:
                    break
        return cls(result)

    def to_bytes(self) -> bytes:
        """ Convert the values to bytes. """
        return Int32(len(self.values)).to_bytes() + b"".join(
            value.to_bytes() for value in self.values
        )

    def write(self, stream: io.BytesIO) -> io.BytesIO:
        """ Write the bytes representation of a value into a binary stream. """
        stream.write(self.to_bytes())
        return stream

    def validate(self) -> None:
        """Validate all values.

        Raises:
            DataValidationError: If the value is not a collection of `scalar_type` objects.
        """
        for value in self.values:
            if not isinstance(value, self.scalar_type):
                raise DataValidationError(
                    f"{type(self)} requires a collection of {self.scalar_type.__name__} objects"
                )
            value.validate()  # type: ignore

    def __repr__(self):
        return f"<{type(self).__name__} length={len(self.values)}>"

    @classmethod
    def create(
        cls: typing.Type[EncodingProtocolVar],
        serialiser: Type[EncodingTypeVar],
        name,
        parents: typing.Optional[typing.List[str]] = None,
        resolver: Optional[Resolver] = None,
    ) -> typing.Type[EncodingProtocolVar]:
        """Class constructor."""
        resolver = resolver or resolve
        name = pascalcase(f"{resolver.name}{serialiser.__name__}SetSerialiser")
        return cast(
            typing.Type[EncodingProtocolVar],
            type(name, (GenericScalarSetSerialiser,), {"scalar_type": serialiser}),
        )


@dataclasses.dataclass
class KeyValue(typing.Generic[Enc_K, Enc_V]):
    enc_k: typing.Union[str, typing.Type[Enc_K]]
    enc_v: typing.Union[str, typing.Type[Enc_V]]


class GenericMapSerialiser(
    Generic[Enc_K, Enc_V], Dict[Enc_K, Enc_V], EncodingProtocol[KeyValue[Enc_K, Enc_V]]
):
    """Serialiser for a mapping value."""

    key_type: Type[Enc_K]
    value_type: Type[Enc_V]

    def __init__(self, values: Union[dict, Iterable[tuple]]):
        cast_values = {}
        if isinstance(values, dict):
            values = values.items()
        for key, value in values:
            if not isinstance(key, EncodingType):
                key = self.key_type(key)
            if not isinstance(value, EncodingType):
                value = self.value_type(value)
            cast_values[key] = value
        super().__init__(cast_values)
        self.validate()

    @classmethod
    def read(cls, stream: io.BytesIO) -> GenericMapSerialiser:
        """ Read the values from a stream. """
        result = {}
        length = Int32.read(stream).value
        if length:
            for _ in range(length):
                try:
                    key = cls.key_type.read(stream)
                    value = cls.value_type.read(stream)
                except StreamExhausted:  # pragma: no cover
                    break
                else:
                    result[key] = value
        return cls(result)

    def to_bytes(self) -> bytes:
        """ Convert the values to bytes. """
        return Int32(len(self)).to_bytes() + b"".join(
            key.to_bytes() + value.to_bytes() for key, value in self.items()
        )

    def write(self, stream: io.BytesIO) -> io.BytesIO:
        """ Write the bytes representation of a value into a binary stream. """
        stream.write(self.to_bytes())
        return stream

    def validate(self) -> None:
        """ Validate all values. """
        for key, value in self.items():
            if not isinstance(key, self.key_type):
                raise DataValidationError(
                    f"Key {key}: expected {self.key_type}, got {type(key)}."
                )
            key.validate()
            if not isinstance(value, self.value_type):
                raise DataValidationError(
                    f"Value {key}: expected {self.value_type}, got {type(value)}."
                )
            value.validate()

    @property
    def value(self):
        """ All the values; needed for compatibility with `EncodingType`. """
        return self

    def __repr__(self):
        return f"<{type(self).__name__} length={len(self)}>"

    @classmethod
    def create(
        cls: typing.Type[EncodingProtocolVar],
        spec: KeyValue,
        name,
        parents: typing.Optional[typing.List[str]] = None,
        resolver: Optional[Resolver] = None,
    ) -> typing.Type[EncodingProtocolVar]:
        """Class constructor."""
        from .base import resolve

        ks_resolved: Type[Enc_K]
        vs_resolved: Type[Enc_V]
        resolver = resolver or resolve
        key_serialiser = spec.enc_k
        value_serialiser = spec.enc_v
        if isinstance(key_serialiser, str):
            ks_resolved = cast(Type[Enc_K], resolver.specs[key_serialiser])
        else:
            ks_resolved = key_serialiser
        if isinstance(value_serialiser, str):
            vs_resolved = cast(Type[Enc_V], resolver.specs[value_serialiser])
        else:
            vs_resolved = value_serialiser
        name = pascalcase(
            f"{ks_resolved.__name__}{vs_resolved.__name__}MapSerialiser"  # type: ignore
        )
        hashed_name = f"{resolver.name}{name}"
        return cast(
            typing.Type[EncodingProtocolVar],
            type(
                hashed_name,
                (GenericMapSerialiser,),
                {"key_type": ks_resolved, "value_type": vs_resolved},
            ),
        )
