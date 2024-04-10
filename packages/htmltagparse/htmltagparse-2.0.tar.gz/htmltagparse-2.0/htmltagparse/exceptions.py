"""htmltagparse exceptions"""
import time

__all__ = [
    "HtmlHttpError",
    "HtmlTagError",
]

class HtmlHttpError(Exception):
    """Exception for htmltagparse."""
    def __init__(self, *args):
        pass

class HtmlTagError(Exception):
    """Timeout expired."""
    def __init__(self, *args):
        pass
