#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理API接口
"""

from flask import Blueprint, request
from backend.database import execute_query, execute_update, execute_paginated_query
from app.utils import (
    AuthUtils, require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response, conflict_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@require_auth

@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'role': {'type': 'string', 'choices': ['student', 'teacher', 'admin']},
    'status': {'type': 'string', 'choices': ['active', 'inactive']},
    'search': {'type': 'string', 'max_length': 100}
})
def get_users():
    """获取用户列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['page_size']
        role = params.get('role')
        status = params.get('status')
        search = params.get('search')
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        if role:
            where_conditions.append('role = %s')
            query_params.append(role)
        
        if status:
            where_conditions.append('status = %s')
            query_params.append(status)
        
        if search:
            where_conditions.append('(username LIKE %s OR name LIKE %s OR email LIKE %s)')
            search_param = f'%{search}%'
            query_params.extend([search_param, search_param, search_param])
        
        # 构建SQL
        base_sql = """
        SELECT id, username, name, email, phone, role, status, created_at, updated_at
        FROM users
        """
        
        if where_conditions:
            base_sql += ' WHERE ' + ' AND '.join(where_conditions)
        
        base_sql += ' ORDER BY created_at DESC'
        
        # 执行分页查询
        result = execute_paginated_query(base_sql, tuple(query_params), page, page_size)
        
        if not result['success']:
            logger.error(f"查询用户列表失败: {result.get('error')}")
            return error_response("获取用户列表失败")
        
        # 格式化数据
        users = []
        for user in result['data']:
            users.append({
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'role': user['role'],
                'status': user['status'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None,
                'updated_at': user['updated_at'].isoformat() if user['updated_at'] else None
            })
        
        return paginated_response(users, result['pagination'], "获取用户列表成功")
        
    except Exception as e:
        logger.error(f"获取用户列表接口错误: {str(e)}")
        return error_response("获取用户列表失败")

@users_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
def get_user(user_id):
    """获取用户详情"""
    try:
        sql = """
        SELECT id, username, name, email, phone, role, status, created_at, updated_at
        FROM users 
        WHERE id = %s
        """
        result = execute_query(sql, (user_id,))
        
        if not result['success']:
            logger.error(f"查询用户详情失败: {result.get('error')}")
            return error_response("获取用户详情失败")
        
        if not result['data']:
            return not_found_response("用户不存在")
        
        user = result['data'][0]
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role'],
            'status': user['status'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'updated_at': user['updated_at'].isoformat() if user['updated_at'] else None
        }
        
        return success_response(user_info, "获取用户详情成功")
        
    except Exception as e:
        logger.error(f"获取用户详情接口错误: {str(e)}")
        return error_response("获取用户详情失败")

@users_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin'])
@validate_json_data({
    'username': {'required': True, 'type': 'string', 'min_length': 3, 'max_length': 50},
    'password': {'required': True, 'type': 'password', 'min_length': 6},
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'email': {'required': True, 'type': 'email'},
    'phone': {'required': False, 'type': 'phone'},
    'role': {'required': True, 'type': 'string', 'choices': ['student', 'teacher', 'admin']},
    'status': {'required': False, 'type': 'string', 'choices': ['active', 'inactive']}
})
def create_user():
    """创建用户"""
    try:
        data = request.validated_data
        username = data['username']
        password = data['password']
        name = data['name']
        email = data['email']
        phone = data.get('phone')
        role = data['role']
        status = data.get('status', 'active')
        
        # 检查用户名是否已存在
        check_sql = "SELECT id FROM users WHERE username = %s"
        check_result = execute_query(check_sql, (username,))
        
        if not check_result['success']:
            logger.error(f"检查用户名失败: {check_result.get('error')}")
            return error_response("创建用户失败，请稍后重试")
        
        if check_result['data']:
            return conflict_response("用户名已存在")
        
        # 检查邮箱是否已存在
        email_check_sql = "SELECT id FROM users WHERE email = %s"
        email_check_result = execute_query(email_check_sql, (email,))
        
        if not email_check_result['success']:
            logger.error(f"检查邮箱失败: {email_check_result.get('error')}")
            return error_response("创建用户失败，请稍后重试")
        
        if email_check_result['data']:
            return conflict_response("邮箱已被使用")
        
        # 哈希密码
        hashed_password = AuthUtils.hash_password(password)
        
        # 插入新用户
        insert_sql = """
        INSERT INTO users (username, password, name, email, phone, role, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        insert_result = execute_update(insert_sql, (username, hashed_password, name, email, phone, role, status))
        
        if not insert_result['success']:
            logger.error(f"创建用户失败: {insert_result.get('error')}")
            return error_response("创建用户失败，请稍后重试")
        
        # 获取新创建的用户信息
        user_id = insert_result['last_insert_id']
        user_sql = """
        SELECT id, username, name, email, phone, role, status, created_at
        FROM users 
        WHERE id = %s
        """
        user_result = execute_query(user_sql, (user_id,))
        
        if user_result['success'] and user_result['data']:
            user = user_result['data'][0]
            user_info = {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'role': user['role'],
                'status': user['status'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            }
            
            return created_response(user_info, "用户创建成功")
        
        return created_response(None, "用户创建成功")
        
    except Exception as e:
        logger.error(f"创建用户接口错误: {str(e)}")
        return error_response("创建用户失败，请稍后重试")

@users_bp.route('/<int:user_id>', methods=['PUT'])
@require_auth
@require_role(['admin'])
@validate_json_data({
    'name': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'email': {'required': False, 'type': 'email'},
    'phone': {'required': False, 'type': 'phone'},
    'role': {'required': False, 'type': 'string', 'choices': ['student', 'teacher', 'admin']},
    'status': {'required': False, 'type': 'string', 'choices': ['active', 'inactive']}
})
def update_user(user_id):
    """更新用户信息"""
    try:
        data = request.validated_data
        
        # 检查用户是否存在
        check_sql = "SELECT id FROM users WHERE id = %s"
        check_result = execute_query(check_sql, (user_id,))
        
        if not check_result['success']:
            return error_response("更新失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("用户不存在")
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        if 'name' in data and data['name'] is not None:
            update_fields.append('name = %s')
            update_values.append(data['name'])
        
        if 'email' in data and data['email'] is not None:
            # 检查邮箱是否已被其他用户使用
            email_check_sql = "SELECT id FROM users WHERE email = %s AND id != %s"
            email_check_result = execute_query(email_check_sql, (data['email'], user_id))
            
            if not email_check_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if email_check_result['data']:
                return conflict_response("邮箱已被其他用户使用")
            
            update_fields.append('email = %s')
            update_values.append(data['email'])
        
        if 'phone' in data and data['phone'] is not None:
            update_fields.append('phone = %s')
            update_values.append(data['phone'])
        
        if 'role' in data and data['role'] is not None:
            update_fields.append('role = %s')
            update_values.append(data['role'])
        
        if 'status' in data and data['status'] is not None:
            update_fields.append('status = %s')
            update_values.append(data['status'])
        
        if not update_fields:
            return error_response("没有需要更新的字段")
        
        # 添加更新时间
        update_fields.append('updated_at = NOW()')
        update_values.append(user_id)
        
        # 执行更新
        update_sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        update_result = execute_update(update_sql, tuple(update_values))
        
        if not update_result['success']:
            logger.error(f"更新用户信息失败: {update_result.get('error')}")
            return error_response("更新失败，请稍后重试")
        
        # 获取更新后的用户信息
        user_sql = """
        SELECT id, username, name, email, phone, role, status, created_at, updated_at
        FROM users 
        WHERE id = %s
        """
        user_result = execute_query(user_sql, (user_id,))
        
        if user_result['success'] and user_result['data']:
            user = user_result['data'][0]
            user_info = {
                'id': user['id'],
                'username': user['username'],
                'name': user['name'],
                'email': user['email'],
                'phone': user['phone'],
                'role': user['role'],
                'status': user['status'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None,
                'updated_at': user['updated_at'].isoformat() if user['updated_at'] else None
            }
            
            return updated_response(user_info, "用户信息更新成功")
        
        return updated_response(None, "用户信息更新成功")
        
    except Exception as e:
        logger.error(f"更新用户信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_user(user_id):
    """删除用户"""
    try:
        # 检查用户是否存在
        check_sql = "SELECT id, username FROM users WHERE id = %s"
        check_result = execute_query(check_sql, (user_id,))
        
        if not check_result['success']:
            return error_response("删除失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("用户不存在")
        
        # 防止删除自己
        current_user_id = request.current_user.get('id') or request.current_user.get('user_id')
        if user_id == current_user_id:
            return error_response("不能删除自己的账户")
        
        # 删除用户
        delete_sql = "DELETE FROM users WHERE id = %s"
        delete_result = execute_update(delete_sql, (user_id,))
        
        if not delete_result['success']:
            logger.error(f"删除用户失败: {delete_result.get('error')}")
            return error_response("删除失败，请稍后重试")
        
        return deleted_response("用户删除成功")
        
    except Exception as e:
        logger.error(f"删除用户接口错误: {str(e)}")
        return error_response("删除失败，请稍后重试")

@users_bp.route('/<int:user_id>/reset-password', methods=['PUT'])
@require_auth
@require_role(['admin'])
@validate_json_data({
    'new_password': {'required': True, 'type': 'password', 'min_length': 6}
})
def reset_user_password(user_id):
    """重置用户密码"""
    try:
        data = request.validated_data
        new_password = data['new_password']
        
        # 检查用户是否存在
        check_sql = "SELECT id FROM users WHERE id = %s"
        check_result = execute_query(check_sql, (user_id,))
        
        if not check_result['success']:
            return error_response("重置密码失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("用户不存在")
        
        # 哈希新密码
        hashed_password = AuthUtils.hash_password(new_password)
        
        # 更新密码
        update_sql = "UPDATE users SET password = %s, updated_at = NOW() WHERE id = %s"
        update_result = execute_update(update_sql, (hashed_password, user_id))
        
        if not update_result['success']:
            logger.error(f"重置密码失败: {update_result.get('error')}")
            return error_response("重置密码失败，请稍后重试")
        
        return success_response(None, "密码重置成功")
        
    except Exception as e:
        logger.error(f"重置密码接口错误: {str(e)}")
        return error_response("重置密码失败，请稍后重试")
