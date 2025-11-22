#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程管理API接口
"""

from flask import Blueprint, request
from backend.init_database import execute_query, execute_update, execute_paginated_query, execute_transaction, execute_transaction
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response, conflict_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
courses_bp = Blueprint('courses', __name__)

@courses_bp.route('', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'teacher_id': {'type': 'integer', 'min_value': 1},
    'semester': {'type': 'string', 'max_length': 20},
    'status': {'type': 'string', 'choices': ['active', 'inactive', 'completed']},
    'search': {'type': 'string', 'max_length': 100}
})
def get_courses():
    """获取课程列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['page_size']
        teacher_id = params.get('teacher_id')
        semester = params.get('semester')
        status = params.get('status')
        search = params.get('search')
        
        current_user = request.current_user
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        # 教师只能查看自己的课程
        if current_user['role'] == 'teacher':
            teacher_id = current_user['id']
        
        if teacher_id:
            where_conditions.append('c.teacher_id = %s')
            query_params.append(teacher_id)
        
        if semester:
            where_conditions.append('c.semester = %s')
            query_params.append(semester)
        
        if status:
            where_conditions.append('c.status = %s')
            query_params.append(status)
        
        if search:
            where_conditions.append('(c.name LIKE %s OR c.code LIKE %s OR c.description LIKE %s)')
            search_param = f'%{search}%'
            query_params.extend([search_param, search_param, search_param])
        
        # 构建SQL
        # 检查课程表是否有实验室相关字段
        has_cols = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='courses' AND COLUMN_NAME IN ('requires_lab','laboratory_id') LIMIT 1"
        )
        has_lab_fields = has_cols.get('success') and bool(has_cols.get('data'))
        if has_lab_fields:
            base_sql = """
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester,
                   c.status, c.created_at, c.updated_at,
                   c.requires_lab, c.laboratory_id,
                   u.name as teacher_name, u.email as teacher_email,
                   l.name as laboratory_name
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            LEFT JOIN laboratories l ON c.laboratory_id = l.id
            """
        else:
            base_sql = """
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester, 
                   c.status, c.created_at, c.updated_at,
                   u.name as teacher_name, u.email as teacher_email
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            """
        
        if where_conditions:
            base_sql += ' WHERE ' + ' AND '.join(where_conditions)
        
        base_sql += ' ORDER BY c.semester DESC, c.name ASC'
        
        # 执行分页查询
        result = execute_paginated_query(base_sql, tuple(query_params), page, page_size)
        
        if not result['success']:
            logger.error(f"查询课程列表失败: {result.get('error')}")
            return error_response("获取课程列表失败")
        
        # 格式化数据
        courses = []
        for course in result['data']:
            # 获取课程学生数量
            student_count_sql = "SELECT COUNT(*) as count FROM course_students WHERE course_id = %s"
            student_count_result = execute_query(student_count_sql, (course['id'],))
            student_count = 0
            if student_count_result['success'] and student_count_result['data']:
                student_count = student_count_result['data'][0]['count']
            
            item = {
                'id': course['id'],
                'name': course['name'],
                'code': course['code'],
                'description': course['description'],
                'credits': course['credits'],
                'semester': course['semester'],
                'status': course['status'],
                'student_count': student_count,
                'teacher': {
                    'name': course['teacher_name'],
                    'email': course['teacher_email']
                } if course['teacher_name'] else None,
                'created_at': course['created_at'].isoformat() if course['created_at'] else None,
                'updated_at': course['updated_at'].isoformat() if course['updated_at'] else None
            }
            if has_lab_fields:
                item['requires_lab'] = bool(course.get('requires_lab'))
                item['laboratory_id'] = course.get('laboratory_id')
                item['laboratory_name'] = course.get('laboratory_name')
            courses.append(item)
        
        return paginated_response(courses, result['pagination'], "获取课程列表成功")
        
    except Exception as e:
        logger.error(f"获取课程列表接口错误: {str(e)}")
        return error_response("获取课程列表失败")

@courses_bp.route('/<int:course_id>', methods=['GET'])
@require_auth
def get_course(course_id):
    """获取课程详情"""
    try:
        current_user = request.current_user
        
        # 构建查询条件
        where_condition = "c.id = %s"
        query_params = [course_id]
        
        # 教师只能查看自己的课程
        if current_user['role'] == 'teacher':
            where_condition += " AND c.teacher_id = %s"
            query_params.append(current_user['id'])
        
        has_cols = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='courses' AND COLUMN_NAME IN ('requires_lab','laboratory_id') LIMIT 1"
        )
        has_lab_fields = has_cols.get('success') and bool(has_cols.get('data'))
        if has_lab_fields:
            sql = f"""
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester,
                   c.status, c.created_at, c.updated_at,
                   c.teacher_id, u.name as teacher_name, u.email as teacher_email,
                   c.requires_lab, c.laboratory_id, l.name as laboratory_name
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            LEFT JOIN laboratories l ON c.laboratory_id = l.id
            WHERE {where_condition}
            """
        else:
            sql = f"""
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester, 
                   c.status, c.created_at, c.updated_at,
                   c.teacher_id, u.name as teacher_name, u.email as teacher_email
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE {where_condition}
            """
        
        result = execute_query(sql, tuple(query_params))
        
        if not result['success']:
            logger.error(f"查询课程详情失败: {result.get('error')}")
            return error_response("获取课程详情失败")
        
        if not result['data']:
            return not_found_response("课程不存在")
        
        course = result['data'][0]
        
        # 获取课程学生列表
        students_sql = """
        SELECT u.id, u.name, u.email, u.student_id, cs.enrolled_at
        FROM course_students cs
        JOIN users u ON cs.student_id = u.id
        WHERE cs.course_id = %s
        ORDER BY u.name ASC
        """
        students_result = execute_query(students_sql, (course_id,))
        
        students = []
        if students_result['success']:
            for student in students_result['data']:
                students.append({
                    'id': student['id'],
                    'name': student['name'],
                    'email': student['email'],
                    'student_id': student['student_id'],
                    'enrolled_at': student['enrolled_at'].isoformat() if student['enrolled_at'] else None
                })
        
        course_info = {
            'id': course['id'],
            'name': course['name'],
            'code': course['code'],
            'description': course['description'],
            'credits': course['credits'],
            'semester': course['semester'],
            'status': course['status'],
            'teacher_id': course['teacher_id'],
            'teacher': {
                'name': course['teacher_name'],
                'email': course['teacher_email']
            } if course['teacher_name'] else None,
            'students': students,
            'student_count': len(students),
            'created_at': course['created_at'].isoformat() if course['created_at'] else None,
            'updated_at': course['updated_at'].isoformat() if course['updated_at'] else None
        }
        if has_lab_fields:
            course_info['requires_lab'] = bool(course.get('requires_lab'))
            course_info['laboratory_id'] = course.get('laboratory_id')
            course_info['laboratory_name'] = course.get('laboratory_name')
        
        return success_response(course_info, "获取课程详情成功")
        
    except Exception as e:
        logger.error(f"获取课程详情接口错误: {str(e)}")
        return error_response("获取课程详情失败")

@courses_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'code': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 20},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'credits': {'required': True, 'type': 'integer', 'min_value': 1, 'max_value': 10},
    'semester': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 20},
    'teacher_id': {'required': False, 'type': 'integer', 'min_value': 1},
    'status': {'required': False, 'type': 'string', 'choices': ['active', 'inactive', 'completed']},
    'requires_lab': {'required': False, 'type': 'integer', 'min_value': 0, 'max_value': 1},
    'laboratory_id': {'required': False, 'type': 'integer', 'min_value': 1}
})
def create_course():
    """创建课程"""
    try:
        data = request.validated_data
        current_user = request.current_user
        
        name = data['name']
        code = data['code']
        description = data.get('description', '')
        credits = data['credits']
        semester = data['semester']
        status = data.get('status', 'active')
        requires_lab_flag = int(data.get('requires_lab') or 0)
        requires_lab = 1 if requires_lab_flag == 1 else 0
        laboratory_id = data.get('laboratory_id')
        
        # 确定教师ID
        if current_user['role'] == 'admin':
            teacher_id = data.get('teacher_id')
            if teacher_id:
                # 验证教师是否存在
                teacher_check_sql = "SELECT id FROM users WHERE id = %s AND role = 'teacher'"
                teacher_result = execute_query(teacher_check_sql, (teacher_id,))
                
                if not teacher_result['success']:
                    return error_response("创建课程失败，请稍后重试")
                
                if not teacher_result['data']:
                    return error_response("指定的教师不存在")
        else:
            # 教师创建课程时，自动设置为自己
            teacher_id = current_user['id']
        
        # 检查课程代码是否已存在
        code_check_sql = "SELECT id FROM courses WHERE code = %s AND semester = %s"
        code_result = execute_query(code_check_sql, (code, semester))
        
        if not code_result['success']:
            return error_response("创建课程失败，请稍后重试")
        
        if code_result['data']:
            return conflict_response("该学期已存在相同课程代码")
        
        # 验证实验室（如果需要）
        if requires_lab == 1:
            if not laboratory_id:
                return error_response("请选择关联实验室")
            lab_check = execute_query("SELECT id FROM laboratories WHERE id = %s", (laboratory_id,))
            if not (lab_check['success'] and lab_check['data']):
                return not_found_response("关联实验室不存在")

        # 插入新课程（兼容无新列的环境）
        has_cols = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='courses' AND COLUMN_NAME='requires_lab' LIMIT 1"
        )
        has_lab_fields = has_cols.get('success') and bool(has_cols.get('data'))
        if has_lab_fields:
            insert_sql = """
            INSERT INTO courses (name, code, description, credits, semester, teacher_id, status, requires_lab, laboratory_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            insert_result = execute_update(insert_sql, (
                name, code, description, credits, semester, teacher_id, status, requires_lab, laboratory_id
            ))
        else:
            insert_sql = """
            INSERT INTO courses (name, code, description, credits, semester, teacher_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            insert_result = execute_update(insert_sql, (
                name, code, description, credits, semester, teacher_id, status
            ))
        
        if not insert_result['success']:
            logger.error(f"创建课程失败: {insert_result.get('error')}")
            return error_response("创建课程失败，请稍后重试")
        
        # 获取新创建的课程信息
        course_id = insert_result['last_insert_id']
        if has_lab_fields:
            course_sql = """
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester,
                   c.status, c.created_at,
                   c.requires_lab, c.laboratory_id,
                   u.name as teacher_name, u.email as teacher_email,
                   l.name as laboratory_name
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            LEFT JOIN laboratories l ON c.laboratory_id = l.id
            WHERE c.id = %s
            """
        else:
            course_sql = """
            SELECT c.id, c.name, c.code, c.description, c.credits, c.semester, 
                   c.status, c.created_at,
                   u.name as teacher_name, u.email as teacher_email
            FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE c.id = %s
            """
        course_result = execute_query(course_sql, (course_id,))
        
        if course_result['success'] and course_result['data']:
            course = course_result['data'][0]
            course_info = {
                'id': course['id'],
                'name': course['name'],
                'code': course['code'],
                'description': course['description'],
                'credits': course['credits'],
                'semester': course['semester'],
                'status': course['status'],
                'teacher': {
                    'name': course['teacher_name'],
                    'email': course['teacher_email']
                } if course['teacher_name'] else None,
                'student_count': 0,
                'created_at': course['created_at'].isoformat() if course['created_at'] else None
            }
            if has_lab_fields:
                course_info['requires_lab'] = bool(course.get('requires_lab'))
                course_info['laboratory_id'] = course.get('laboratory_id')
                course_info['laboratory_name'] = course.get('laboratory_name')
            
            return created_response(course_info, "课程创建成功")
        
        return created_response(None, "课程创建成功")
        
    except Exception as e:
        logger.error(f"创建课程接口错误: {str(e)}")
        return error_response("创建课程失败，请稍后重试")

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'code': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 20},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'credits': {'required': False, 'type': 'integer', 'min_value': 1, 'max_value': 10},
    'semester': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 20},
    'teacher_id': {'required': False, 'type': 'integer', 'min_value': 1},
    'status': {'required': False, 'type': 'string', 'choices': ['active', 'inactive', 'completed']},
    'requires_lab': {'required': False, 'type': 'integer', 'min_value': 0, 'max_value': 1},
    'laboratory_id': {'required': False, 'type': 'integer', 'min_value': 1}
})
def update_course(course_id):
    """更新课程信息"""
    try:
        data = request.validated_data
        current_user = request.current_user
        
        # 检查课程是否存在
        check_sql = "SELECT id, teacher_id, semester FROM courses WHERE id = %s"
        check_result = execute_query(check_sql, (course_id,))
        
        if not check_result['success']:
            return error_response("更新失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("课程不存在")
        
        course = check_result['data'][0]
        
        # 权限检查：教师只能修改自己的课程
        if (current_user['role'] == 'teacher' and 
            current_user['id'] != course['teacher_id']):
            return error_response("没有权限修改此课程")
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        if 'name' in data and data['name'] is not None:
            update_fields.append('name = %s')
            update_values.append(data['name'])
        
        if 'code' in data and data['code'] is not None:
            # 检查课程代码是否已被其他课程使用（同一学期）
            semester_to_check = data.get('semester', course['semester'])
            code_check_sql = "SELECT id FROM courses WHERE code = %s AND semester = %s AND id != %s"
            code_check_result = execute_query(code_check_sql, (data['code'], semester_to_check, course_id))
            
            if not code_check_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if code_check_result['data']:
                return conflict_response("该学期已存在相同课程代码")
            
            update_fields.append('code = %s')
            update_values.append(data['code'])
        
        if 'description' in data and data['description'] is not None:
            update_fields.append('description = %s')
            update_values.append(data['description'])
        
        if 'credits' in data and data['credits'] is not None:
            update_fields.append('credits = %s')
            update_values.append(data['credits'])
        
        if 'semester' in data and data['semester'] is not None:
            # 如果修改学期，需要重新检查课程代码冲突
            if 'code' not in data:  # 如果没有同时修改code，需要检查当前code在新学期是否冲突
                current_code_sql = "SELECT code FROM courses WHERE id = %s"
                current_code_result = execute_query(current_code_sql, (course_id,))
                
                if current_code_result['success'] and current_code_result['data']:
                    current_code = current_code_result['data'][0]['code']
                    code_check_sql = "SELECT id FROM courses WHERE code = %s AND semester = %s AND id != %s"
                    code_check_result = execute_query(code_check_sql, (current_code, data['semester'], course_id))
                    
                    if code_check_result['success'] and code_check_result['data']:
                        return conflict_response("该学期已存在相同课程代码")
            
            update_fields.append('semester = %s')
            update_values.append(data['semester'])
        
        if 'teacher_id' in data and data['teacher_id'] is not None:
            # 只有管理员可以修改教师
            if current_user['role'] != 'admin':
                return error_response("没有权限修改课程教师")
            
            # 验证教师是否存在
            teacher_check_sql = "SELECT id FROM users WHERE id = %s AND role = 'teacher'"
            teacher_result = execute_query(teacher_check_sql, (data['teacher_id'],))
            
            if not teacher_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if not teacher_result['data']:
                return error_response("指定的教师不存在")
            
            update_fields.append('teacher_id = %s')
            update_values.append(data['teacher_id'])
        
        if 'status' in data and data['status'] is not None:
            update_fields.append('status = %s')
            update_values.append(data['status'])

        # 课程实验室设置
        has_cols = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='courses' AND COLUMN_NAME='requires_lab' LIMIT 1"
        )
        has_lab_fields = has_cols.get('success') and bool(has_cols.get('data'))
        if has_lab_fields:
            if 'requires_lab' in data and data['requires_lab'] is not None:
                rl = 1 if int(data['requires_lab']) == 1 else 0
                update_fields.append('requires_lab = %s')
                update_values.append(rl)
                # 如果不需要实验室，清空 laboratory_id
                if rl == 0:
                    update_fields.append('laboratory_id = %s')
                    update_values.append(None)
            if 'laboratory_id' in data:
                lab_id = data.get('laboratory_id')
                if lab_id is not None:
                    # 验证实验室存在
                    lab_check = execute_query("SELECT id FROM laboratories WHERE id = %s", (lab_id,))
                    if not (lab_check['success'] and lab_check['data']):
                        return not_found_response("关联实验室不存在")
                update_fields.append('laboratory_id = %s')
                update_values.append(lab_id)
        
        if not update_fields:
            return error_response("没有需要更新的字段")
        
        # 添加更新时间
        update_fields.append('updated_at = NOW()')
        update_values.append(course_id)
        
        # 执行更新
        update_sql = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
        update_result = execute_update(update_sql, tuple(update_values))
        
        if not update_result['success']:
            logger.error(f"更新课程信息失败: {update_result.get('error')}")
            return error_response("更新失败，请稍后重试")
        
        return updated_response(None, "课程信息更新成功")
        
    except Exception as e:
        logger.error(f"更新课程信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_course(course_id):
    """删除课程"""
    try:
        # 检查课程是否存在
        check_sql = "SELECT id, name FROM courses WHERE id = %s"
        check_result = execute_query(check_sql, (course_id,))
        
        if not check_result['success']:
            return error_response("删除失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("课程不存在")
        
        # 检查课程是否有学生
        student_check_sql = "SELECT COUNT(*) as count FROM course_students WHERE course_id = %s"
        student_result = execute_query(student_check_sql, (course_id,))
        
        if student_result['success'] and student_result['data']:
            student_count = student_result['data'][0]['count']
            if student_count > 0:
                return error_response("该课程有学生选课记录，无法删除")
        
        # 使用事务删除课程及相关数据
        delete_operations = [
            ("DELETE FROM course_students WHERE course_id = %s", (course_id,)),
            ("DELETE FROM courses WHERE id = %s", (course_id,))
        ]
        
        transaction_result = execute_transaction(delete_operations)
        
        if not transaction_result['success']:
            logger.error(f"删除课程失败: {transaction_result.get('error')}")
            return error_response("删除失败，请稍后重试")
        
        return deleted_response("课程删除成功")
        
    except Exception as e:
        logger.error(f"删除课程接口错误: {str(e)}")
        return error_response("删除失败，请稍后重试")

@courses_bp.route('/<int:course_id>/students', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'student_ids': {'required': True, 'type': 'list', 'min_length': 1}
})
def add_students_to_course(course_id):
    """添加学生到课程"""
    try:
        data = request.validated_data
        current_user = request.current_user
        student_ids = data['student_ids']
        
        # 检查课程是否存在
        check_sql = "SELECT id, teacher_id, name FROM courses WHERE id = %s"
        check_result = execute_query(check_sql, (course_id,))
        
        if not check_result['success']:
            return error_response("操作失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("课程不存在")
        
        course = check_result['data'][0]
        
        # 权限检查：教师只能操作自己的课程
        if (current_user['role'] == 'teacher' and 
            current_user['id'] != course['teacher_id']):
            return error_response("没有权限操作此课程")
        
        # 验证学生是否存在
        student_check_sql = """
        SELECT id FROM users 
        WHERE id IN ({}) AND role = 'student'
        """.format(','.join(['%s'] * len(student_ids)))
        
        student_result = execute_query(student_check_sql, tuple(student_ids))
        
        if not student_result['success']:
            return error_response("操作失败，请稍后重试")
        
        valid_student_ids = [row['id'] for row in student_result['data']]
        
        if len(valid_student_ids) != len(student_ids):
            return error_response("部分学生不存在或不是学生角色")
        
        # 检查哪些学生已经选了这门课
        existing_check_sql = """
        SELECT student_id FROM course_students 
        WHERE course_id = %s AND student_id IN ({})
        """.format(','.join(['%s'] * len(student_ids)))
        
        existing_params = [course_id] + student_ids
        existing_result = execute_query(existing_check_sql, tuple(existing_params))
        
        existing_student_ids = []
        if existing_result['success']:
            existing_student_ids = [row['student_id'] for row in existing_result['data']]
        
        # 过滤出需要添加的学生
        new_student_ids = [sid for sid in student_ids if sid not in existing_student_ids]
        
        if not new_student_ids:
            return error_response("所有学生都已经选了这门课")
        
        # 批量插入新的选课记录
        insert_operations = []
        for student_id in new_student_ids:
            insert_operations.append((
                "INSERT INTO course_students (course_id, student_id, enrolled_at) VALUES (%s, %s, NOW())",
                (course_id, student_id)
            ))
        
        transaction_result = execute_transaction(insert_operations)
        
        if not transaction_result['success']:
            logger.error(f"添加学生到课程失败: {transaction_result.get('error')}")
            return error_response("添加学生失败，请稍后重试")
        
        result_info = {
            'added_count': len(new_student_ids),
            'skipped_count': len(existing_student_ids),
            'total_requested': len(student_ids)
        }
        
        message = f"成功添加{len(new_student_ids)}名学生"
        if existing_student_ids:
            message += f"，跳过{len(existing_student_ids)}名已选课学生"
        
        return created_response(result_info, message)
        
    except Exception as e:
        logger.error(f"添加学生到课程接口错误: {str(e)}")
        return error_response("添加学生失败，请稍后重试")

@courses_bp.route('/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
@require_auth
@require_role(['admin', 'teacher'])
def remove_student_from_course(course_id, student_id):
    """从课程中移除学生"""
    try:
        current_user = request.current_user
        
        # 检查课程是否存在
        check_sql = "SELECT id, teacher_id, name FROM courses WHERE id = %s"
        check_result = execute_query(check_sql, (course_id,))
        
        if not check_result['success']:
            return error_response("操作失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("课程不存在")
        
        course = check_result['data'][0]
        
        # 权限检查：教师只能操作自己的课程
        if (current_user['role'] == 'teacher' and 
            current_user['id'] != course['teacher_id']):
            return error_response("没有权限操作此课程")
        
        # 检查学生是否在该课程中
        enrollment_check_sql = """
        SELECT id FROM course_students 
        WHERE course_id = %s AND student_id = %s
        """
        enrollment_result = execute_query(enrollment_check_sql, (course_id, student_id))
        
        if not enrollment_result['success']:
            return error_response("操作失败，请稍后重试")
        
        if not enrollment_result['data']:
            return not_found_response("该学生未选择此课程")
        
        # 删除选课记录
        delete_sql = "DELETE FROM course_students WHERE course_id = %s AND student_id = %s"
        delete_result = execute_update(delete_sql, (course_id, student_id))
        
        if not delete_result['success']:
            logger.error(f"移除学生失败: {delete_result.get('error')}")
            return error_response("移除学生失败，请稍后重试")
        
        return deleted_response("学生移除成功")
        
    except Exception as e:
        logger.error(f"移除学生接口错误: {str(e)}")
        return error_response("移除学生失败，请稍后重试")

@courses_bp.route('/my-courses', methods=['GET'])
@require_auth
@require_role(['student'])
def get_my_courses():
    """获取我的课程（学生用）"""
    try:
        current_user = request.current_user
        
        sql = """
        SELECT c.id, c.name, c.code, c.description, c.credits, c.semester, 
               c.status, cs.enrolled_at,
               u.name as teacher_name, u.email as teacher_email
        FROM course_students cs
        JOIN courses c ON cs.course_id = c.id
        LEFT JOIN users u ON c.teacher_id = u.id
        WHERE cs.student_id = %s
        ORDER BY c.semester DESC, c.name ASC
        """
        
        result = execute_query(sql, (current_user['id'],))
        
        if not result['success']:
            logger.error(f"查询学生课程失败: {result.get('error')}")
            return error_response("获取课程列表失败")
        
        courses = []
        for course in result['data']:
            courses.append({
                'id': course['id'],
                'name': course['name'],
                'code': course['code'],
                'description': course['description'],
                'credits': course['credits'],
                'semester': course['semester'],
                'status': course['status'],
                'teacher': {
                    'name': course['teacher_name'],
                    'email': course['teacher_email']
                } if course['teacher_name'] else None,
                'enrolled_at': course['enrolled_at'].isoformat() if course['enrolled_at'] else None
            })
        
        return success_response(courses, "获取我的课程成功")
        
    except Exception as e:
        logger.error(f"获取学生课程接口错误: {str(e)}")
        return error_response("获取课程列表失败")