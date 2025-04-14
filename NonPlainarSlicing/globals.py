class Glob:
    """
    A static container for global progress values used to update progress bars 
    in the application's user interface.

    This class holds shared progress indicators that can be accessed and modified 
    from anywhere in the codebase without needing to pass instances around.

    Progress values are clamped between 0 and 1 (i.e., 0% to 100%).

    Attributes:
        progress (float): Primary progress value (0 to 1).
        progress2 (float): Secondary progress value (0 to 1).
    """


    _progress = 0.0
    _step_progress = 1

    _progress2 = 0.0
    _step_progress2 = 1

    @classmethod
    def get_progress(cls) -> float:
        """Get the current value of primary progress."""
        return cls._progress

    @classmethod
    def set_progress(cls, value: float) -> None:
        """Set the value of primary progress, clamped between 0 and 1."""
        cls._progress = max(0.0, min(1.0, value))

    @classmethod
    def get_progress2(cls) -> float:
        """Get the current value of secondary progress."""
        return cls._progress2

    @classmethod
    def set_progress2(cls, value: float) -> None:
        """Set the value of secondary progress, clamped between 0 and 1."""
        cls._progress2 = max(0.0, min(1.0, value))

    @classmethod
    def initialize_progress(cls, number_steps) -> None:
        cls._step_progress = 1 / number_steps
        cls.set_progress(0)

    @classmethod
    def initialize_progress_2(cls, number_steps) -> None:
        cls._step_progress2 = 1 / number_steps
        cls.set_progress2(0)

    @classmethod
    def progressed(cls) -> None:
        cls.set_progress(cls._progress + cls._step_progress)

    @classmethod
    def progressed_2(cls) -> None:
        cls.set_progress2(cls._progress2 + cls._step_progress2)
