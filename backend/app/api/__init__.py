#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API模块初始化文件
"""

from .auth import auth_bp
from .users import users_bp
from .laboratories import laboratories_bp
from .equipment import equipment_bp
from .reservations import reservations_bp
from .courses import courses_bp
from .maintenance import maintenance_bp

__all__ = [
    'auth_bp',
    'users_bp', 
    'laboratories_bp',
    'equipment_bp',
    'reservations_bp',
    'courses_bp',
    'maintenance_bp'
]