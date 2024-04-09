#  Copyright (c) 2022 - 2024 DiffusionData Ltd., All Rights Reserved.
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
import inspect
import io
import typing

import typing_extensions
import dataclasses

import stringcase

import diffusion.datatypes
from diffusion.handlers import LOG
from diffusion.internal.utils import BaseConfig, decode

if typing.TYPE_CHECKING:  # pragma: no cover
    from diffusion.internal.services.abstract import (
        ServiceValue,
    )
    from diffusion.internal.serialisers.base import Serialiser, Resolver
    from .attrs import MarshalledModel as AttrsModel
    from .pydantic import MarshalledModel as PydanticModel

    Model_Variants = typing.Union[AttrsModel, PydanticModel]
    Model_Variants_T = typing.TypeVar("Model_Variants_T", bound=Model_Variants)

GenericModel_T = typing.TypeVar("GenericModel_T", bound="GenericModel")
GenericModel_T_Other = typing.TypeVar("GenericModel_T_Other", bound="GenericModel")


class GenericConfig(
    typing.Generic[GenericModel_T],
    BaseConfig,
):
    """
    Adds Serialiser support to Model.Config
    'alias' defines the name of the serialiser to map to
    """

    alias: typing.ClassVar[str]
    allow_population_by_field_name = True
    alias_generator = stringcase.spinalcase

    @classmethod
    def verify_item(cls, item: ServiceValue, modelcls: typing.Type[GenericModel_T]):
        try:
            assert item._serialiser.name in cls.attr_mappings_all(modelcls)
        except Exception as e:  # pragma: no cover
            LOG.error(f"Got exception {e}")
            raise

    @classmethod
    @functools.lru_cache(maxsize=None)
    def serialiser(cls, name=None, resolver: typing.Optional[Resolver] = None) -> "Serialiser":
        from diffusion.internal.serialisers.base import Serialiser

        if not name:
            if not isinstance(getattr(cls, "alias", None), str):
                raise RuntimeError(f"{cls} has no 'alias'")
        return Serialiser.by_name(name or cls.alias, resolver=resolver)

    @classmethod
    def to_bytes(
        cls, item: GenericModel_T, serialiser: typing.Optional[Serialiser] = None
    ) -> bytes:
        serialiser = cls.check_serialiser(serialiser)
        as_tuple = cls.as_tuple(item, serialiser=serialiser)
        return serialiser.to_bytes(*as_tuple)

    @classmethod
    def check_serialiser(cls, serialiser: typing.Optional[Serialiser]) -> Serialiser:
        from diffusion.internal.serialisers.base import Serialiser
        if serialiser is None:
            return cls.serialiser()
        assert isinstance(serialiser, Serialiser)
        return serialiser

    @classmethod
    def from_service_value(
        cls,
        modelcls: typing.Type[GenericModel_T],
        item: ServiceValue,
    ) -> GenericModel_T:
        fields = cls.get_fields(item, modelcls)
        try:
            return modelcls.from_fields(**fields)
        except Exception as e:  # pragma: no cover
            LOG.error(f"Got exception {e}")
            raise

    @classmethod
    def get_fields(cls, item, modelcls):
        cls.verify_item(item, modelcls)
        mapping = cls.get_model_to_serialiser_mapping(
            modelcls, serialiser=item._serialiser
        )
        fields = cls.gen_fields(
            item,
            mapping,
            modelcls,
        )
        try:
            assert fields
            assert all(x is not None for x in fields.keys())
        except Exception as e:  # pragma: no cover
            LOG.error(f"Got exception {e}")
            raise
        return fields

    @classmethod
    def gen_fields(cls, item, model_to_serialiser_mapping, modelcls):
        try:
            result = {
                model_key: modelcls.Config.decode(
                    item[serialiser.name],
                    modelcls,
                    model_key=model_key,
                    serialiser=serialiser,
                )
                for model_key, serialiser in model_to_serialiser_mapping.items()
                if serialiser
            }
            assert all(x is not None for x in result.keys())
            return result
        except Exception as e:  # pragma: no cover
            LOG.error(f"Got exception {e}")
            raise

    @classmethod
    def from_tuple(
        cls,
        modelcls: typing.Type[GenericModel_T],
        tp: typing.Tuple[typing.Any, ...],
        serialiser: typing.Optional[Serialiser] = None
    ) -> GenericModel_T:
        serialiser = cls.check_serialiser(serialiser)
        sv = cls.service_value(serialiser).evolve(*tp)
        result = cls.from_service_value(modelcls, sv)
        return result

    @classmethod
    def fields_from_tuple(
        cls,
        modelcls: typing.Type[GenericModel_T_Other],
        tp: typing.Tuple[typing.Any, ...],
        serialiser: typing.Optional[Serialiser] = None,
    ) -> typing.Mapping[str, typing.Any]:
        sv = cls.service_value(serialiser).evolve(*tp)
        result = cls.get_fields(sv, modelcls)
        return result

    @classmethod
    def read(
        cls,
        modelcls: typing.Type[GenericModel_T],
        stream: io.BytesIO,
        serialiser: typing.Optional[Serialiser] = None,
    ) -> GenericModel_T:
        serialiser = cls.check_serialiser(serialiser)
        return cls.from_tuple(
            modelcls, tuple(serialiser.read(stream)), serialiser
        )

    @classmethod
    @functools.lru_cache(maxsize=None)
    def find_aliases(
        cls, modelcls: typing.Type[GenericModel_T], serialiser: Serialiser
    ) -> typing.Mapping[str, str]:
        return {}

    @classmethod
    @functools.lru_cache(maxsize=None)
    def get_model_to_serialiser_mapping(
        cls,
        modelcls: typing.Type[Model_Variants],
        serialiser: typing.Optional[Serialiser] = None,
    ) -> typing.Mapping[str, Serialiser]:
        try:
            serialiser = cls.check_serialiser(serialiser)
            final_mapping = modelcls.Config.attr_mappings_final(
                modelcls, serialiser=serialiser
            )
            result = {}
            for serialiser_key, model_key in final_mapping.items():
                final_model_key = getattr(model_key, "__name__", model_key)
                final_serialiser_key = cls.sanitize_key(serialiser_key, serialiser)
                if not (final_serialiser_key and final_model_key):
                    continue
                result.update(
                    {
                        final_model_key: cls.serialiser(
                            final_serialiser_key, resolver=serialiser.resolver
                        )
                    }
                )

            assert all(x is not None for x in result.keys())
            assert all(x is not None for x in result.values())
            return result
        except Exception as e:  # pragma: no cover
            raise e

    @classmethod
    def sanitize_key(cls, name: str, serialiser: typing.Optional[Serialiser] = None):
        sv = cls.service_value(serialiser)
        result = sv.sanitize_key(name)
        if result:
            return result
        if cls.alias_generator:
            result = sv.sanitize_key(cls.alias_generator(name))
        if not result:  # pragma: no cover
            LOG.error(f"Couldn't find {name} in {sv.spec}")
        return result

    @classmethod
    def get_service_value_args(cls, item: Model_Variants, serialiser=None):
        model_to_serialiser_mapping = cls.get_model_to_serialiser_mapping(
            type(item), serialiser=serialiser
        )
        try:
            mappings = {
                v.name: cls.as_service_value_field(getattr(item, k), serialiser=v)
                for k, v in model_to_serialiser_mapping.items()
            }  # NOQA
        except Exception as e:  # pragma: no cover
            raise e
        return mappings

    @classmethod
    def decode(
        cls,
        item,
        modelcls: typing.Type[GenericModel_T],
        model_key: str,
        serialiser: typing.Optional[Serialiser] = None,
    ):
        return decode(item)

    @classmethod
    def get_field_type(cls, modelcls: typing.Type[Model_Variants], model_key: str):
        result = typing_extensions.get_type_hints(modelcls).get(model_key)
        return result

    @classmethod
    def decode_complex(
        cls,
        item,
        modelcls: typing.Type[Model_Variants],
        model_key: str,
        serialiser: Serialiser,
    ) -> typing.Optional[typing.List]:
        from diffusion.internal.serialisers.base import ListEncoder

        if len(serialiser.spec.values()) == 1:
            sub_encoder = next(iter(serialiser.spec.values()), None)

            if inspect.isclass(sub_encoder):
                if issubclass(sub_encoder, ListEncoder):
                    item_type = cls.get_field_type(modelcls, model_key).__args__[0]

                    return sub_encoder.from_tuple(item, item_type)
        return None

    @classmethod
    def as_service_value_field(cls, item: GenericModel_T, serialiser: Serialiser):
        from diffusion.internal.serialisers.base import (
            ListEncoder,
            ChoiceEncoder,
        )

        sub_encoder = serialiser.get_encoder(ListEncoder, ChoiceEncoder)
        if sub_encoder:
            return sub_encoder.as_tuple(item)

        if isinstance(item, diffusion.datatypes.AbstractDataType):
            return item.encode(item.value)
        if isinstance(item, GenericModel):
            return item.Config.as_tuple(item, serialiser)
        return item

    @classmethod
    def as_service_value(
        cls: typing.Type[GenericConfig[GenericModel_T]],
        item: GenericModel_T,
        serialiser: typing.Optional[Serialiser] = None,
    ) -> ServiceValue:
        sv = cls.service_value(serialiser)
        mappings = cls.get_service_value_args(
            typing.cast("Model_Variants", item), serialiser=serialiser
        )
        try:
            return sv.evolve(**mappings)
        except Exception as e:  # pragma: no cover
            LOG.error(f"Caught exception {e}")
            raise

    @classmethod
    def as_tuple(
        cls, item: GenericModel_T, serialiser: typing.Optional[Serialiser] = None
    ) -> typing.Tuple[typing.Any, ...]:
        return tuple(item.Config.as_service_value(item, serialiser=serialiser).values())

    @classmethod
    @functools.lru_cache(maxsize=None)
    def attr_mappings_final(
        cls,
        modelcls: typing.Type[Model_Variants],
        serialiser: typing.Optional[Serialiser] = None,
    ) -> typing.Dict[str, typing.Any]:
        try:
            serialiser = cls.check_serialiser(serialiser)
            attr_mapping = cls.attr_mappings_all(modelcls).get(serialiser.name)
            result = {**(attr_mapping or {})}
            updates = cls.find_aliases(modelcls, serialiser)
            result.update({k: v for k, v in updates.items() if k and v})
            assert all([x for x in result.keys()])
            assert all([x for x in result.values()])
            return result
        except Exception as e:  # pragma: no cover
            raise e

    @classmethod
    @functools.lru_cache(maxsize=None)
    def service_value(cls, serialiser: typing.Optional[Serialiser] = None):
        from diffusion.internal.services.abstract import ServiceValue

        return ServiceValue(cls.check_serialiser(serialiser))

    @classmethod
    def attr_mappings_all(cls, modelcls):
        return {cls.alias: {}}

    @classmethod
    def entry_from_list_of_choices_as_tuple(
        cls, event: GenericModel, serialiser: Serialiser
    ):
        from diffusion.internal.serialisers.base import (
            ListEncoder,
            ChoiceEncoder,
        )

        choice_encoder = ChoiceEncoder.extract_from(
            serialiser.to_encoder(ListEncoder).serialiser
        )
        return choice_encoder.as_tuple(event)


ModelFields_T = typing.TypeVar("ModelFields_T", bound="ModelFields")


@dataclasses.dataclass
class ModelFields(object):
    @classmethod
    def from_fields(cls: typing.Type[ModelFields_T], kwargs: typing.Any) -> ModelFields_T:
        kwargs_fields = {
            field.name: kwargs.pop(field.name) for field in dataclasses.fields(cls)
        }
        fields = cls(**kwargs_fields)  # type: ignore
        return fields


class GenericModel(object):
    class Config(GenericConfig):
        pass

    def to_bytes(self) -> bytes:
        return self.Config.to_bytes(self)

    @classmethod
    def from_fields(cls: typing.Type[GenericModel_T], **kwargs) -> GenericModel_T:
        # noinspection PyArgumentList
        try:
            return cls(**kwargs)
        except Exception as e:  # pragma: no cover
            LOG.error(f"Got exception {e}")
            raise

    @classmethod
    def from_service_value(
        cls: typing.Type[GenericModel_T], item: ServiceValue
    ) -> GenericModel_T:
        return cls.Config.from_service_value(cls, item)

    @classmethod
    def from_tuple(
        cls: typing.Type[GenericModel],
        tp: typing.Tuple[typing.Any, ...],
        serialiser: typing.Optional[Serialiser] = None
    ):
        result = cls.Config.from_tuple(cls, tp, serialiser=serialiser)
        return result


class GenericMetaModel(type):
    Config: typing.Type[GenericConfig]

    # noinspection PyAbstractClass
    def __new__(
        mcs,
        name: str,
        bases: typing.Tuple[type, ...],
        namespace: typing.Dict[str, typing.Any],
        **kwds,
    ) -> typing.Type[GenericModel]:
        result = super().__new__(mcs, name, bases, namespace, **kwds)

        class ConcreteConfig(result.Config):  # type: ignore
            _modelcls = result

        result.Config = ConcreteConfig
        return typing.cast(typing.Type[GenericModel], result)
