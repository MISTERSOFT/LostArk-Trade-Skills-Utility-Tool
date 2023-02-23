from .singleton import MetaSingleton
from .log_service import LogService

LogService = LogService()

__all__ = ["MetaSingleton", "LogService"]
