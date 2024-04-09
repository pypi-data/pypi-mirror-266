"""
Инициализирует пакет
"""

from importlib.metadata import PackageNotFoundError, version
from .schema import *  # импорт схемы swagger для пакета

try:
    __version__ = version("email-auth-remote")
except PackageNotFoundError:
    # package is not installed
    __version__ = None  # type: ignore[assignment]
