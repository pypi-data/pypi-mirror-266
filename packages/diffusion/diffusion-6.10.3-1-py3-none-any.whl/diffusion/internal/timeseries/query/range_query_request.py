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

import dataclasses
import typing

import diffusion.internal.pydantic_compat.v1 as pydantic

from diffusion.internal.serialisers.generic_model import ModelFields
from diffusion.internal.timeseries.query.range_query_parameters import (
    RangeQueryParameters,
    QueryType,
    Range,
    Point,
)
from diffusion.internal.serialisers.pydantic import MarshalledModel


class RangeQueryRequest(MarshalledModel):
    """
    The range query request.

    Since:
        6.9
    """

    topic_path: pydantic.StrictStr
    """
    The topic path
    """

    parameters: RangeQueryParameters
    """
    The range query paraemters
    """

    @property
    def type(self) -> int:
        return self.parameters.query_type

    @property
    def view_range_anchor(self):
        return self.parameters.view_range.anchor

    @property
    def view_range_span(self):
        return self.parameters.view_range.span

    @property
    def edit_range_anchor(self):
        return self.parameters.edit_range.anchor

    @property
    def edit_range_span(self):
        return self.parameters.edit_range.span

    def __str__(self):
        return (
            f"{type(self.parameters).__name__}.DEFAULT_RANGE_QUERY()"
            f'{self.parameters}.select_from("{self.topic_path}")'
        )

    class Config(MarshalledModel.Config):
        frozen = True

        @classmethod
        def attr_mappings_all(cls, modelcls):
            # fmt: off
            return {
                "range-query-request": {
                    "path": "topic_path",
                    "range-query-parameters.range-query-type": "type",
                    "range-query-parameters.view-range.range-query-range.range-query-anchor":
                        "view_range_anchor",
                    "range-query-parameters.view-range.range-query-range.range-query-span":
                        "view_range_span",
                    "range-query-parameters.edit-range.range-query-range.range-query-anchor":
                        "edit_range_anchor",
                    "range-query-parameters.edit-range.range-query-range.range-query-span":
                        "edit_range_span",
                    "range-query-parameters.limit": "limit",
                }
            }
            # fmt: on

    @property
    def limit(self):
        return self.parameters.limit

    @classmethod
    def from_fields(
        cls: typing.Type[RangeQueryRequest],
        **kwargs,
    ) -> RangeQueryRequest:
        @dataclasses.dataclass
        class RangeQueryFields(ModelFields):
            type: int
            topic_path: str
            view_range_anchor: Point
            view_range_span: Point
            edit_range_anchor: Point
            edit_range_span: Point

        fields = RangeQueryFields.from_fields(kwargs)
        limit = None
        query_type = QueryType(fields.type)
        final_args = dict(
            query_type=query_type,
            view_range=Range(fields.view_range_anchor, fields.view_range_span),
            edit_range=Range(fields.edit_range_anchor, fields.edit_range_span),
            limit=limit,
        )
        parameters = RangeQueryParameters(
            **{k: v for k, v in final_args.items() if v is not None}
        )
        return RangeQueryRequest(topic_path=fields.topic_path, parameters=parameters)
