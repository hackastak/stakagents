"""The common agent interface. Every agent is a typed input -> output unit."""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class Agent(ABC, Generic[InputT, OutputT]):
    """Base class for every agent in the fleet.

    Subclasses declare:
      - name:          registry key AND the API route (POST /agents/{name}/run)
      - input_model:   Pydantic model — the typed request / tool-call schema
      - output_model:  Pydantic model — the typed response
      - run():         the actual logic, input instance -> output instance
    """

    name: ClassVar[str]
    input_model: ClassVar[type[BaseModel]]
    output_model: ClassVar[type[BaseModel]]

    @abstractmethod
    def run(self, payload: InputT) -> OutputT:
        """Execute the agent. Tracing is automatic via the shared core."""
