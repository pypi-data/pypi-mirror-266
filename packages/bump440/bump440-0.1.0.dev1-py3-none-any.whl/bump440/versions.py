# src/bump440/versions.py
import toml
from packaging import version as packaging_version
from .io import get_pyproject
from .logger import get_logger

logger = get_logger(__name__)


class Version:
    def __init__(self):
        self.pyproject = get_pyproject()
        self.current_version = packaging_version.Version(
            self.pyproject["project"]["version"]
        )

    def save(self, new_version):
        self.pyproject["project"]["version"] = str(new_version)
        with open("pyproject.toml", "w") as f:
            toml.dump(self.pyproject, f)


class CurrentVersion(Version):
    """
    Get the current version of the project from pyproject.toml.
    """

    def get(self):
        return self.current_version


class NextVersion(Version):
    """
    Base class for bumping the version of the project.
    """

    def bump(self):
        raise NotImplementedError("Subclasses must implement this method.")


class Epoch(NextVersion):
    """
    Bump the epoch part of the version.
    """

    def bump(self):
        new_version = packaging_version.Version(str(self.current_version.epoch + 1))
        self.save(new_version)


class Release(NextVersion):
    """
    Bump the release part of the version.
    """

    def bump_major(self):
        new_version = packaging_version.Version(
            str(self.current_version.release[0] + 1) + ".0.0"
        )
        self.save(new_version)

    def bump_minor(self):
        new_version = packaging_version.Version(
            str(self.current_version.release[0])
            + "."
            + str(self.current_version.release[1] + 1)
            + ".0"
        )
        self.save(new_version)

    def bump_micro(self):
        new_version = packaging_version.Version(
            str(self.current_version.release[0])
            + "."
            + str(self.current_version.release[1])
            + "."
            + str(self.current_version.release[2] + 1)
        )
        self.save(new_version)


class Pre(NextVersion):
    """
    Bump the pre-release part of the version.
    """

    def bump(self):
        new_version = packaging_version.Version(str(self.current_version) + "a1")
        self.save(new_version)


class Post(NextVersion):
    """
    Bump the post-release part of the version.
    """

    def bump(self):
        new_version = packaging_version.Version(str(self.current_version) + ".post1")
        self.save(new_version)


class Dev(NextVersion):
    """
    Bump the development release part of the version.
    """

    def bump(self):
        new_version = packaging_version.Version(str(self.current_version) + ".dev1")
        self.save(new_version)
