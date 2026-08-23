"""Agent registry — the single source of truth the service builds routes from."""

from stakagents.core.agent import Agent

_registry: dict[str, Agent] = {}


def register(cls: type[Agent]) -> type[Agent]:
    """Class decorator: instantiate an agent and register it by its name."""
    instance = cls()
    if instance.name in _registry:
        raise ValueError(f"agent already registered: {instance.name!r}")
    _registry[instance.name] = instance
    return cls


def get(name: str) -> Agent:
    if name not in _registry:
        raise KeyError(f"unknown agent: {name!r}")
    return _registry[name]


def all_agents() -> dict[str, Agent]:
    return dict(_registry)
