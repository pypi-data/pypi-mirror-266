"""
This module lists the decorators for error handling.
"""
# Python standard library imports
import sys


def handle_error(func):
    """
    A decorator function for error handling.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    return wrapper
