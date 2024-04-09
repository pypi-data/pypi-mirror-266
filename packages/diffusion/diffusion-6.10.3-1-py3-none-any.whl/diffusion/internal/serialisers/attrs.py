#  Copyright (c) 2022 - 2023 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

from __future__ import annotations

import functools
import typing

import attr

from diffusion.handlers import LOG
from diffusion.internal.serialisers.generic_model import (
    GenericModel,
    GenericMetaModel,
    GenericConfig,
)

if typing.TYPE_CHECKING:
    from diffusion.internal.services import ServiceValue
    from diffusion.internal.serialisers import Serialiser

AttrsModel_T = typing.TypeVar("AttrsModel_T", bound="MarshalledModel")
AttrsModel_T_Other = typing.TypeVar("AttrsModel_T_Other", bound="MarshalledModel")


@attr.s
class MarshalledModel(GenericModel, metaclass=GenericMetaModel):
    class Config(GenericConfig["MarshalledModel"]):
        _modelcls: typing.Type[MarshalledModel]

        @classmethod
        @functools.lru_cache(maxsize=None)
        def find_aliases(
            cls, modelcls: typing.Type[MarshalledModel], serialiser: Serialiser
        ) -> typing.Mapping[str, str]:
            serialiser = cls.check_serialiser(serialiser)
            updates = {}
            for x in attr.fields(modelcls):
                if x.metadata:
                    target = x.metadata.get(
                        getattr(serialiser, "name") or cls.alias, x.metadata.get("alias")
                    )
                    updates[target] = x.name
            return updates

        @classmethod
        def from_service_value(
            cls,
            modelcls: typing.Type[MarshalledModel],
            item: ServiceValue,
        ) -> MarshalledModel:
            fields = cls.get_fields(item, modelcls)
            for field_name, field_value in fields.items():
                try:
                    field = attr.fields_dict(modelcls).get(field_name)
                    if field and field.converter:
                        fields[field.name] = field.converter(fields[field.name])
                except Exception as e:  # pragma: no cover
                    LOG.error(f"Got exception {e}")
                    raise
            try:
                return modelcls.from_fields(
                    **fields
                )
            except Exception as e:  # pragma: no cover
                LOG.error(f"Got exception {e}")
                raise
