#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证和JWT工具模块
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        try:
            # 生成盐值并哈希密码
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"密码哈希失败: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False
    
    @staticmethod
    def generate_token(user_data: Dict[str, Any], expires_in: int = None) -> str:
        """生成JWT令牌"""
        try:
            # 获取配置
            secret_key = current_app.config['SECRET_KEY']
            
            # 如果未指定过期时间，使用配置或默认值
            if expires_in is None:
                expires_in_raw = os.getenv('JWT_EXPIRES_IN', '86400')
                expires_in = AuthUtils._parse_expires_in(expires_in_raw)
            
            # 构建payload
            payload = {
                'user_id': user_data.get('id'),
                'username': user_data.get('username'),
                'role': user_data.get('role', 'student'),
                'type': user_data.get('type', 'access'),  # 添加令牌类型
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            # 生成token
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return token
        except Exception as e:
            logger.error(f"JWT令牌生成失败: {str(e)}")
            raise

    @staticmethod
    def generate_reset_token(user_id: int, email: str) -> str:
        """生成重置密码令牌 (有效期1小时)"""
        return AuthUtils.generate_token({
            'id': user_id,
            'username': email,  # 复用username字段存储email，或者忽略
            'role': 'guest',
            'type': 'reset'
        }, expires_in=3600)


    @staticmethod 
    def _parse_expires_in(value: str) -> int:
        """将过期时间字符串解析为秒数。
        支持纯数字秒、以及带单位的值：s(秒)、m(分钟)、h(小时)、d(天)。
        例如："3600"、"15m"、"24h"、"7d"。
        解析失败时，回退为 86400 秒（24 小时）。
        """
        try:
            if value is None:
                return 86400
            s = str(value).strip().lower()
            # 纯数字，按秒处理
            if s.isdigit():
                seconds = int(s)
                return seconds if seconds > 0 else 86400
            # 带单位
            if s.endswith('s'):
                num = int(s[:-1])
                return num if num > 0 else 86400
            if s.endswith('m'):
                num = int(s[:-1])
                return num * 60 if num > 0 else 86400
            if s.endswith('h'):
                num = int(s[:-1])
                return num * 3600 if num > 0 else 86400
            if s.endswith('d'):
                num = int(s[:-1])
                return num * 86400 if num > 0 else 86400
            # 未识别格式，尝试直接转换
            seconds = int(s)
            return seconds if seconds > 0 else 86400
        except Exception:
            logger.warning(f"无法解析 JWT_EXPIRES_IN 值 '{value}'，已回退为 86400 秒")
            return 86400
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            secret_key = current_app.config['SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT令牌无效: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT令牌验证失败: {str(e)}")
            return None
    
    @staticmethod
    def get_token_from_header() -> Optional[str]:
        """从请求头获取token"""
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

def require_auth(f):
    """需要认证的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 获取token
            token = AuthUtils.get_token_from_header()
            if not token:
                return jsonify({
                    'success': False,
                    'message': '缺少认证令牌',
                    'code': 'MISSING_TOKEN'
                }), 401
            
            # 验证token
            payload = AuthUtils.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'message': '认证令牌无效或已过期',
                    'code': 'INVALID_TOKEN'
                }), 401
            
            # 将用户信息添加到请求上下文
            request.current_user = payload
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"认证装饰器错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': '认证失败',
                'code': 'AUTH_ERROR'
            }), 500
    
    return decorated_function

def require_role(required_roles: Union[str, list]):
    """需要特定角色的装饰器"""
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 首先检查是否已认证
                if not hasattr(request, 'current_user'):
                    return jsonify({
                        'success': False,
                        'message': '需要先进行身份认证',
                        'code': 'AUTH_REQUIRED'
                    }), 401
                
                # 检查角色权限
                user_role = request.current_user.get('role')
                if user_role not in required_roles:
                    return jsonify({
                        'success': False,
                        'message': '权限不足',
                        'code': 'INSUFFICIENT_PERMISSIONS'
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"角色权限装饰器错误: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '权限检查失败',
                    'code': 'PERMISSION_ERROR'
                }), 500
        
        return decorated_function
    return decorator

def optional_auth(f):
    """可选认证装饰器（不强制要求认证）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 尝试获取token
            token = AuthUtils.get_token_from_header()
            if token:
                # 如果有token，尝试验证
                payload = AuthUtils.verify_token(token)
                if payload:
                    request.current_user = payload
                else:
                    request.current_user = None
            else:
                request.current_user = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"可选认证装饰器错误: {str(e)}")
            request.current_user = None
            return f(*args, **kwargs)
    
    return decorated_function

def get_current_user() -> Optional[Dict[str, Any]]:
    """获取当前用户信息"""
    return getattr(request, 'current_user', None)

def is_authenticated() -> bool:
    """检查是否已认证"""
    return get_current_user() is not None

def has_role(role: str) -> bool:
    """检查是否具有指定角色"""
    user = get_current_user()
    if not user:
        return False
    return user.get('role') == role

def has_any_role(roles: list) -> bool:
    """检查是否具有任意指定角色"""
    user = get_current_user()
    if not user:
        return False
    return user.get('role') in roles