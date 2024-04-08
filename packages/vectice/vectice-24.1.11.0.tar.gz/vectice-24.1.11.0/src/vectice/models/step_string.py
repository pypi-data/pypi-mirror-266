from __future__ import annotations

from vectice.api.json.step import StepType
from vectice.models.step import Step


class StepString(Step):
    """Model a string step."""

    def __init__(self, step: Step, string: str | None = None):
        """Initialize a string step.

        Parameters:
            step: The step.
            string: The step string.
        """
        super().__init__(
            step.id,
            step._iteration,
            step.name,
            step.index,
            step.slug,
            step._description,
            step_type=StepType.StepString,
            artifacts=step.artifacts,
        )
        self._string = string

    def __repr__(self):
        return f"StepString(name={self.name!r}, id={self.id!r}, description={self._description!r}, string={self._string!r})"

    @property
    def string(self) -> str | None:
        """The step's string.

        Returns:
            The step's string.
        """
        return self._string
