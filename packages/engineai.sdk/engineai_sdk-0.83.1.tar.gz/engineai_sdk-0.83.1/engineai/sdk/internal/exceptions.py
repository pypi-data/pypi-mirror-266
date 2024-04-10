"""Engine AI SDK base Exception."""


class EngineAIBaseSDKError(Exception):
    """Base Exception class for all EngineAI SDK Errors.

    Raises:
        EngineAIBaseSDKError: Platform SDK base error.
    """

    def __init__(self, *args: object) -> None:
        """Base Exception class for all EngineAI SDK Errors."""
        super().__init__(*args)
        self.error_strings = ["EngineAI SDK Error:"]

    def __str__(self) -> str:
        return " ".join(self.error_strings)
