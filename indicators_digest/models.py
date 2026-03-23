from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorReading:
    name: str
    value: int
    label: str
    source_url: str


@dataclass(frozen=True)
class IndicatorFailure:
    name: str
    source_url: str
    error: str
