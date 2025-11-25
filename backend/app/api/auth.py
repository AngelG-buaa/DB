#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证API接口
"""

from flask import Blueprint, request
from backend.database import execute_query, execute_update
from app.utils import (
    AuthUtils, require_auth, validate_json_data, 
    success_response, error_response, unauthorized_response,
    validation_error_response, conflict_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@validate_json_data({
    'username': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 50},
    'password': {'required': True, 'type': 'string', 'min_length': 1}
})
def login():
    """用户登录"""
    try:
        data = request.validated_data
        username = data['username']
        password = data['password']
        
        # 查询用户
        sql = """
        SELECT id, username, password, role, name, email, phone, status, created_at
        FROM users 
        WHERE username = %s AND status = 'active'
        """
        result = execute_query(sql, (username,))
        
        if not result['success']:
            logger.error(f"查询用户失败: {result.get('error')}")
            return error_response("登录失败，请稍后重试")
        
        if not result['data']:
            return unauthorized_response("用户名或密码错误")
        
        user = result['data'][0]
        
        # 验证密码
        if not AuthUtils.verify_password(password, user['password']):
            return unauthorized_response("用户名或密码错误")
        
        # 生成JWT令牌
        token_data = {
            'id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        token = AuthUtils.generate_token(token_data)
        
        # 返回用户信息和令牌
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None
        }
        
        return success_response({
            'token': token,
            'user': user_info
        }, "登录成功")
        
    except Exception as e:
        logger.error(f"登录接口错误: {str(e)}")
        return error_response("登录失败，请稍后重试")

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """用户登出（JWT 为无状态，这里仅返回成功）"""
    try:
        return success_response(None, "退出登录成功")
    except Exception as e:
        logger.error(f"登出接口错误: {str(e)}")
        return error_response("退出登录失败，请稍后重试")

@auth_bp.route('/register', methods=['POST'])
@validate_json_data({
    'username': {'required': True, 'type': 'string', 'min_length': 3, 'max_length': 50},
    'password': {'required': True, 'type': 'password', 'min_length': 6},
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'email': {'required': True, 'type': 'email'},
    'phone': {'required': False, 'type': 'phone'},
    'role': {'required': False, 'type': 'string', 'choices': ['student', 'teacher', 'admin']},
    'course_id': {'required': False, 'type': 'integer', 'min_value': 1}
})
def register():
    """用户注册"""
    try:
        data = request.validated_data
        username = data['username']
        password = data['password']
        name = data['name']
        email = data['email']
        phone = data.get('phone')
        role = data.get('role', 'student')  # 默认为学生角色
        
        # 检查用户名是否已存在
        check_sql = "SELECT id FROM users WHERE username = %s"
        check_result = execute_query(check_sql, (username,))
        
        if not check_result['success']:
            logger.error(f"检查用户名失败: {check_result.get('error')}")
            return error_response("注册失败，请稍后重试")
        
        if check_result['data']:
            return conflict_response("用户名已存在")
        
        # 检查邮箱是否已存在
        email_check_sql = "SELECT id FROM users WHERE email = %s"
        email_check_result = execute_query(email_check_sql, (email,))
        
        if not email_check_result['success']:
            logger.error(f"检查邮箱失败: {email_check_result.get('error')}")
            return error_response("注册失败，请稍后重试")
        
        if email_check_result['data']:
            return conflict_response("邮箱已被使用")
        
        # 哈希密码
        hashed_password = AuthUtils.hash_password(password)
        
        # 插入新用户
        insert_sql = """
        INSERT INTO users (username, password, name, email, phone, role, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'active', NOW())
        """
        insert_result = execute_update(insert_sql, (username, hashed_password, name, email, phone, role))
        
        if not insert_result['success']:
            logger.error(f"创建用户失败: {insert_result.get('error')}")
            return error_response("注册失败，请稍后重试")
        
        # 若为学生且提供了课程，写入选课记录
        try:
            cid = request.get_json().get('course_id') if hasattr(request, 'get_json') else None
        except Exception:
            cid = None
        if role == 'student' and cid:
            # 验证课程存在
            cchk = execute_query("SELECT id FROM courses WHERE id = %s", (cid,))
            if cchk.get('success') and cchk.get('data'):
                _en = execute_update(
                    "INSERT INTO course_students (course_id, student_id, enrolled_at) VALUES (%s, %s, NOW())",
                    (cid, insert_result['last_insert_id'])
                )
                if not _en.get('success'):
                    logger.warning(f"写入课程选课失败: {_en.get('error')}")

        # 获取新创建的用户信息
        user_id = insert_result['last_insert_id']
        user_sql = """
        SELECT id, username, name, email, phone, role, created_at
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
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            }
            
            return success_response(user_info, "注册成功")
        
        return success_response(None, "注册成功")
        
    except Exception as e:
        logger.error(f"注册接口错误: {str(e)}")
        return error_response("注册失败，请稍后重试")

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """获取当前用户信息"""
    try:
        user_id = request.current_user.get('id') or request.current_user.get('user_id')
        
        # 查询用户详细信息
        sql = """
        SELECT id, username, name, email, phone, role, status, created_at, updated_at
        FROM users 
        WHERE id = %s
        """
        result = execute_query(sql, (user_id,))
        
        if not result['success']:
            logger.error(f"查询用户信息失败: {result.get('error')}")
            return error_response("获取用户信息失败")
        
        if not result['data']:
            return unauthorized_response("用户不存在")
        
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
        
        return success_response(user_info, "获取用户信息成功")
        
    except Exception as e:
        logger.error(f"获取用户信息接口错误: {str(e)}")
        return error_response("获取用户信息失败")

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
@validate_json_data({
    'name': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'email': {'required': False, 'type': 'email'},
    'phone': {'required': False, 'type': 'phone'}
})
def update_profile():
    """更新当前用户信息"""
    try:
        user_id = request.current_user.get('id') or request.current_user.get('user_id')
        data = request.validated_data
        
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
        
        if not update_fields:
            return validation_error_response("没有需要更新的字段")
        
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
            
            return success_response(user_info, "更新成功")
        
        return success_response(None, "更新成功")
        
    except Exception as e:
        logger.error(f"更新用户信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@auth_bp.route('/change-password', methods=['PUT'])
@require_auth
@validate_json_data({
    'old_password': {'required': True, 'type': 'string', 'min_length': 1},
    'new_password': {'required': True, 'type': 'password', 'min_length': 6}
})
def change_password():
    """修改密码"""
    try:
        user_id = request.current_user.get('id') or request.current_user.get('user_id')
        data = request.validated_data
        old_password = data['old_password']
        new_password = data['new_password']
        
        # 获取当前密码
        sql = "SELECT password FROM users WHERE id = %s"
        result = execute_query(sql, (user_id,))
        
        if not result['success']:
            logger.error(f"查询用户密码失败: {result.get('error')}")
            return error_response("修改密码失败，请稍后重试")
        
        if not result['data']:
            return unauthorized_response("用户不存在")
        
        current_password = result['data'][0]['password']
        
        # 验证旧密码
        if not AuthUtils.verify_password(old_password, current_password):
            return unauthorized_response("原密码错误")
        
        # 哈希新密码
        new_hashed_password = AuthUtils.hash_password(new_password)
        
        # 更新密码
        update_sql = "UPDATE users SET password = %s, updated_at = NOW() WHERE id = %s"
        update_result = execute_update(update_sql, (new_hashed_password, user_id))
        
        if not update_result['success']:
            logger.error(f"更新密码失败: {update_result.get('error')}")
            return error_response("修改密码失败，请稍后重试")
        
        return success_response(None, "密码修改成功")
        
    except Exception as e:
        logger.error(f"修改密码接口错误: {str(e)}")
        return error_response("修改密码失败，请稍后重试")
