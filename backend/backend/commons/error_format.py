"""Utility functions to format error"""


def format_error(err: Exception) -> dict[str, str]:
    """format Exception object to dict"""
    return {
        'name': type(err).__name__,
        'args': err.args,
        'message': str(err),
    }
