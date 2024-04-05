# src/bump440/exceptions.py


class Bump440Exception(Exception):
    """Base exception for the bump440 package."""

    pass


class ConfigFileNotFoundError(Bump440Exception):
    """Raised when the pyproject.toml file is not found."""

    pass


class TomlDecodeError(Bump440Exception):
    """Raised when there is an error decoding the TOML file."""

    pass


class VersionNotFoundError(Bump440Exception):
    """Raised when the version is not found in the pyproject.toml file."""

    pass


class InvalidPartError(Bump440Exception):
    """Raised when an invalid part is specified."""

    pass
