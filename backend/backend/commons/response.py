"""standard response format"""
from typing import Union


def success_response(data: Union[dict, list], name: str = '', message: str = '') -> dict:
    """format standard success json response"""
    return {
        'success': True,
        'name': name,
        'message': message,
        'data': data,
    }


def failure_response(name: str, message: str, data: dict = None) -> dict:
    """format standard failure json response"""
    return {
        'success': False,
        'name': name,
        'message': message,
        'data': data if data else {},
    }
