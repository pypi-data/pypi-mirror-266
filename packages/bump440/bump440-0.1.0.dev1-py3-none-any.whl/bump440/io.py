# src/bump440/io.py
from pathlib import Path
import toml
from .exceptions import ConfigFileNotFoundError
from .logger import get_logger
from toml import TomlDecodeError

logger = get_logger(__name__)


def is_file(path):
    """
    Check if a file exists.
    :param path:
    :return: True if the file exists.
    """
    if not path.exists():
        raise ConfigFileNotFoundError(f"File not found: {path}")
    return True


def get_pyproject():
    """
    Get the pyproject.toml file and load it.
    :return: The pyproject.toml file as a dictionary.
    """
    toml_path = Path(Path().cwd() / "pyproject.toml")
    if not toml_path.exists():
        logger.error("No pyproject.toml file found.")
        raise ConfigFileNotFoundError("No pyproject.toml file found.")
    logger.debug(f"Found pyproject.toml file at {toml_path}")
    try:
        with open(toml_path, "r") as f:
            pyproject = toml.load(f)
            logger.debug(f"Loaded pyproject.toml file: {pyproject}")
    except TomlDecodeError as e:
        logger.error(f"Error decoding pyproject.toml file: {e}")
        raise TomlDecodeError(f"Error decoding pyproject.toml file: {e}")
    return pyproject
