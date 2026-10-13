"""Stage registry. Stages self-register by name; the runner resolves by name."""
from __future__ import annotations

from typing import Callable, Protocol


class Stage(Protocol):
    name: str
    requires: tuple[str, ...]
    produces: tuple[str, ...]

    def run(self, ctx: "PipelineContext") -> None: ...  # noqa: F821


_REGISTRY: dict[str, Callable[[], Stage]] = {}


def register(name: str) -> Callable[[Callable[[], Stage]], Callable[[], Stage]]:
    def deco(factory: Callable[[], Stage]) -> Callable[[], Stage]:
        if name in _REGISTRY:
            raise ValueError(f"stage {name!r} already registered")
        _REGISTRY[name] = factory
        return factory

    return deco


def get(name: str) -> Stage:
    if name not in _REGISTRY:
        raise KeyError(f"unknown stage {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]()


def names() -> list[str]:
    return sorted(_REGISTRY)