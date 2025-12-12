#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具模块
"""

import re
from typing import Dict, Any, List, Optional, Union
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class Validator:
    """数据验证器"""
    
    @staticmethod
    def is_required(value: Any, field_name: str = "字段") -> Any:
        """必填验证"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValidationError(f"{field_name}不能为空", field_name)
        return value
    
    @staticmethod
    def is_string(value: Any, field_name: str = "字段", min_length: int = 0, max_length: int = None) -> str:
        """字符串验证"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串", field_name)
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name}长度不能少于{min_length}个字符", field_name)
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name}长度不能超过{max_length}个字符", field_name)
        
        return value
    
    @staticmethod
    def is_integer(value: Any, field_name: str = "字段", min_value: int = None, max_value: int = None) -> int:
        """整数验证"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是整数", field_name)
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"{field_name}不能小于{min_value}", field_name)
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"{field_name}不能大于{max_value}", field_name)
        
        return int_value
    
    @staticmethod
    def is_float(value: Any, field_name: str = "字段", min_value: float = None, max_value: float = None) -> float:
        """浮点数验证"""
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是数字", field_name)
        
        if min_value is not None and float_value < min_value:
            raise ValidationError(f"{field_name}不能小于{min_value}", field_name)
        
        if max_value is not None and float_value > max_value:
            raise ValidationError(f"{field_name}不能大于{max_value}", field_name)
        
        return float_value
    
    @staticmethod
    def is_email(value: str, field_name: str = "邮箱") -> str:
        """邮箱验证"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串", field_name)
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(f"{field_name}格式不正确", field_name)
        
        return value
    
    @staticmethod
    def is_phone(value: str, field_name: str = "手机号") -> str:
        """手机号验证"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串", field_name)
        
        phone_pattern = r'^1[3-9]\d{9}$'
        if not re.match(phone_pattern, value):
            raise ValidationError(f"{field_name}格式不正确", field_name)
        
        return value
    
    @staticmethod
    def is_in_choices(value: Any, choices: List[Any], field_name: str = "字段") -> Any:
        """选择项验证"""
        if value not in choices:
            raise ValidationError(f"{field_name}必须是以下值之一: {', '.join(map(str, choices))}", field_name)
        
        return value
    
    @staticmethod
    def is_datetime_string(value: str, field_name: str = "日期时间", format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """日期时间字符串验证"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串", field_name)
        
        from datetime import datetime
        try:
            datetime.strptime(value, format)
        except ValueError:
            raise ValidationError(f"{field_name}格式不正确，应为{format}格式", field_name)
        
        return value
    
    @staticmethod
    def is_date_string(value: str, field_name: str = "日期", format: str = "%Y-%m-%d") -> str:
        """日期字符串验证"""
        return Validator.is_datetime_string(value, field_name, format)
    
    @staticmethod
    def is_password(value: str, field_name: str = "密码", min_length: int = 8) -> str:
        """密码验证"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串", field_name)
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name}长度不能少于{min_length}个字符", field_name)
        
        # 密码复杂度规则：至少包含一个字母和一个数字
        if not re.search(r'[a-zA-Z]', value) or not re.search(r'[0-9]', value):
            raise ValidationError(f"{field_name}必须包含至少一个字母和一个数字", field_name)
        
        return value

def validate_json_data(validation_rules: Dict[str, Dict[str, Any]]):
    """JSON数据验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 获取JSON数据
                if not request.is_json:
                    return jsonify({
                        'success': False,
                        'message': '请求必须是JSON格式',
                        'code': 'INVALID_JSON'
                    }), 400
                
                data = request.get_json()
                if not data:
                    return jsonify({
                        'success': False,
                        'message': '请求数据不能为空',
                        'code': 'EMPTY_DATA'
                    }), 400
                
                # 验证数据
                validated_data = {}
                for field, rules in validation_rules.items():
                    try:
                        value = data.get(field)
                        
                        # 检查必填项
                        if rules.get('required', False):
                            value = Validator.is_required(value, field)
                        elif value is None:
                            # 如果不是必填且值为None，跳过验证
                            validated_data[field] = None
                            continue
                        
                        # 类型验证
                        field_type = rules.get('type')
                        if field_type == 'string':
                            value = Validator.is_string(
                                value, field,
                                rules.get('min_length', 0),
                                rules.get('max_length')
                            )
                        elif field_type == 'integer':
                            value = Validator.is_integer(
                                value, field,
                                rules.get('min_value'),
                                rules.get('max_value')
                            )
                        elif field_type == 'float':
                            value = Validator.is_float(
                                value, field,
                                rules.get('min_value'),
                                rules.get('max_value')
                            )
                        elif field_type == 'email':
                            value = Validator.is_email(value, field)
                        elif field_type == 'phone':
                            value = Validator.is_phone(value, field)
                        elif field_type == 'password':
                            value = Validator.is_password(
                                value, field,
                                rules.get('min_length', 6)
                            )
                        elif field_type == 'datetime':
                            value = Validator.is_datetime_string(
                                value, field,
                                rules.get('format', '%Y-%m-%d %H:%M:%S')
                            )
                        elif field_type == 'date':
                            value = Validator.is_date_string(
                                value, field,
                                rules.get('format', '%Y-%m-%d')
                            )
                        
                        # 选择项验证
                        if 'choices' in rules:
                            value = Validator.is_in_choices(value, rules['choices'], field)
                        
                        validated_data[field] = value
                        
                    except ValidationError as e:
                        return jsonify({
                            'success': False,
                            'message': e.message,
                            'field': e.field,
                            'code': 'VALIDATION_ERROR'
                        }), 400
                
                # 将验证后的数据添加到请求上下文
                request.validated_data = validated_data
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"数据验证装饰器错误: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '数据验证失败',
                    'code': 'VALIDATION_ERROR'
                }), 500
        
        return decorated_function
    return decorator

def validate_query_params(validation_rules: Dict[str, Dict[str, Any]]):
    """查询参数验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 验证查询参数
                validated_params = {}
                for field, rules in validation_rules.items():
                    try:
                        value = request.args.get(field)
                        # 对非必填的空字符串进行处理：视为未提供，使用默认值
                        if not rules.get('required', False) and isinstance(value, str) and value.strip() == "":
                            validated_params[field] = rules.get('default')
                            continue
                        
                        # 检查必填项
                        if rules.get('required', False):
                            value = Validator.is_required(value, field)
                        elif value is None:
                            # 如果不是必填且值为None，使用默认值
                            validated_params[field] = rules.get('default')
                            continue
                        
                        # 类型验证
                        field_type = rules.get('type')
                        if field_type == 'integer':
                            value = Validator.is_integer(
                                value, field,
                                rules.get('min_value'),
                                rules.get('max_value')
                            )
                        elif field_type == 'string':
                            value = Validator.is_string(
                                value, field,
                                rules.get('min_length', 0),
                                rules.get('max_length')
                            )
                        
                        # 选择项验证
                        if 'choices' in rules:
                            value = Validator.is_in_choices(value, rules['choices'], field)
                        
                        validated_params[field] = value
                        
                    except ValidationError as e:
                        return jsonify({
                            'success': False,
                            'message': e.message,
                            'field': e.field,
                            'code': 'VALIDATION_ERROR'
                        }), 400
                
                # 将验证后的参数添加到请求上下文
                request.validated_params = validated_params
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"查询参数验证装饰器错误: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': '参数验证失败',
                    'code': 'VALIDATION_ERROR'
                }), 500
        
        return decorated_function
    return decorator