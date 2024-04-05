# src/bump440/parts.py
from enum import Enum
from .logger import get_logger

logger = get_logger(__name__)


class Part(Enum):
    CURRENT = "current"
    EPOCH = "epoch"
    MAJOR = "major"
    MINOR = "minor"
    MICRO = "micro"
    PRE = "pre"
    POST = "post"
    DEV = "dev"
