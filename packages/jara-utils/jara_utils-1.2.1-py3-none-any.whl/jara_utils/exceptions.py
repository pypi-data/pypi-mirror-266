class JaraError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __unicode__(self) -> str:  # pragma: no cover
        return self.message


class EnvironmentVariableNotFoundError(JaraError):
    """Raise this exception when an environment variable is not defined, but should be."""

    def __init__(self, variable_name: str) -> None:
        super().__init__(f'Environment variable with name {variable_name} not found!')
