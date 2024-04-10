"""Graphql Dataclasses Exceptions."""


class UnauthenticatedError(Exception):
    """Unauthenticated Exception."""

    def __init__(self):
        """Constructor for UnauthenticatedError class."""
        super().__init__(
            "Authentication is required, please use 'engineai login' to authenticate "
            "you access."
        )
