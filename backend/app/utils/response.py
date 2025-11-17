#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一响应格式工具模块
"""

from flask import jsonify
from typing import Any, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ResponseHelper:
    """响应助手类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: str = "SUCCESS") -> tuple:
        """成功响应"""
        response = {
            'success': True,
            'message': message,
            'code': code
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), 200
    
    @staticmethod
    def error(message: str = "操作失败", code: str = "ERROR", status_code: int = 400, 
              data: Any = None) -> tuple:
        """错误响应"""
        response = {
            'success': False,
            'message': message,
            'code': code
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def paginated_success(data: list, pagination: Dict[str, Any], 
                         message: str = "查询成功", code: str = "SUCCESS") -> tuple:
        """分页成功响应"""
        response = {
            'success': True,
            'message': message,
            'code': code,
            'data': data,
            'pagination': pagination
        }
        
        return jsonify(response), 200
    
    @staticmethod
    def validation_error(message: str, field: str = None) -> tuple:
        """验证错误响应"""
        response = {
            'success': False,
            'message': message,
            'code': 'VALIDATION_ERROR'
        }
        
        if field:
            response['field'] = field
        
        return jsonify(response), 400
    
    @staticmethod
    def unauthorized(message: str = "未授权访问") -> tuple:
        """未授权响应"""
        return ResponseHelper.error(message, "UNAUTHORIZED", 401)
    
    @staticmethod
    def forbidden(message: str = "权限不足") -> tuple:
        """禁止访问响应"""
        return ResponseHelper.error(message, "FORBIDDEN", 403)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> tuple:
        """资源不存在响应"""
        return ResponseHelper.error(message, "NOT_FOUND", 404)
    
    @staticmethod
    def conflict(message: str = "资源冲突") -> tuple:
        """资源冲突响应"""
        return ResponseHelper.error(message, "CONFLICT", 409)
    
    @staticmethod
    def internal_error(message: str = "服务器内部错误") -> tuple:
        """服务器内部错误响应"""
        return ResponseHelper.error(message, "INTERNAL_ERROR", 500)
    
    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> tuple:
        """创建成功响应"""
        response = {
            'success': True,
            'message': message,
            'code': 'CREATED'
        }
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), 201
    
    @staticmethod
    def updated(data: Any = None, message: str = "更新成功") -> tuple:
        """更新成功响应"""
        return ResponseHelper.success(data, message, "UPDATED")
    
    @staticmethod
    def deleted(message: str = "删除成功") -> tuple:
        """删除成功响应"""
        return ResponseHelper.success(None, message, "DELETED")

# 便捷函数
def success_response(data: Any = None, message: str = "操作成功", code: str = "SUCCESS") -> tuple:
    """成功响应便捷函数"""
    return ResponseHelper.success(data, message, code)

def error_response(message: str = "操作失败", code: str = "ERROR", status_code: int = 400, 
                  data: Any = None) -> tuple:
    """错误响应便捷函数"""
    return ResponseHelper.error(message, code, status_code, data)

def paginated_response(data: list, pagination: Dict[str, Any], 
                      message: str = "查询成功", code: str = "SUCCESS") -> tuple:
    """分页响应便捷函数"""
    return ResponseHelper.paginated_success(data, pagination, message, code)

def validation_error_response(message: str, field: str = None) -> tuple:
    """验证错误响应便捷函数"""
    return ResponseHelper.validation_error(message, field)

def unauthorized_response(message: str = "未授权访问") -> tuple:
    """未授权响应便捷函数"""
    return ResponseHelper.unauthorized(message)

def forbidden_response(message: str = "权限不足") -> tuple:
    """禁止访问响应便捷函数"""
    return ResponseHelper.forbidden(message)

def not_found_response(message: str = "资源不存在") -> tuple:
    """资源不存在响应便捷函数"""
    return ResponseHelper.not_found(message)

def conflict_response(message: str = "资源冲突") -> tuple:
    """资源冲突响应便捷函数"""
    return ResponseHelper.conflict(message)

def internal_error_response(message: str = "服务器内部错误") -> tuple:
    """服务器内部错误响应便捷函数"""
    return ResponseHelper.internal_error(message)

def created_response(data: Any = None, message: str = "创建成功") -> tuple:
    """创建成功响应便捷函数"""
    return ResponseHelper.created(data, message)

def updated_response(data: Any = None, message: str = "更新成功") -> tuple:
    """更新成功响应便捷函数"""
    return ResponseHelper.updated(data, message)

def deleted_response(message: str = "删除成功") -> tuple:
    """删除成功响应便捷函数"""
    return ResponseHelper.deleted(message)