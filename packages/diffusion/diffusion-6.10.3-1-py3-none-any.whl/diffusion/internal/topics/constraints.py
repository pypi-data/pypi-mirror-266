from __future__ import annotations

from enum import IntEnum


class UpdateConstraintType(IntEnum):

    UNCONSTRAINED_CONSTRAINT = 0
    CONJUNCTION_CONSTRAINT = 1
    BINARY_VALUE_CONSTRAINT = 2
    NO_VALUE_CONSTRAINT = 3
    LOCKED_CONSTRAINT = 4
    NO_TOPIC_CONSTRAINT = 5
    PARTIAL_JSON_CONSTRAINT = 6
