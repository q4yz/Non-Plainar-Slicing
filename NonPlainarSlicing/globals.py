from dataclasses import dataclass


class ProgressTracker:
    """
    Tracks the progress of a process based on a total number of steps.
    """

    def __init__(self, total_steps: int = 1):
        self._progress = 0.0
        self._step_progress = 1 / total_steps if total_steps > 0 else 1

    def get_progress(self) -> float:
        """Get the current progress value (0.0 to 1.0)."""
        return self._progress

    def set_progress(self, value: float) -> None:
        """Set the progress manually, clamped between 0 and 1."""
        self._progress = max(0.0, min(1.0, value))

    def initialize(self, total_steps: int) -> None:
        """Initialize the progress tracker for a new number of steps."""
        self._step_progress = 1 / total_steps if total_steps > 0 else 1
        self.set_progress(0)

    def step(self) -> None:
        """Advance the progress by one step."""
        self.set_progress(self._progress + self._step_progress)


@dataclass()
class Settings:
    resolution: float
    max_depth: int
    max_p: float




class Glob:
    """

    """
    _settings =  Settings(1,10,30)
    _main_tracker = ProgressTracker()
    _sub_tracker = ProgressTracker()

    @classmethod
    def get_main_tracker(cls) -> ProgressTracker:
        """Get the current value of primary progress."""
        return cls._main_tracker

    @classmethod
    def get_sub_tracker(cls) -> ProgressTracker:
        """Get the current value of primary progress."""
        return cls._sub_tracker

    @classmethod
    def get_settings(cls) -> Settings:
        return cls._settings

