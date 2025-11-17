#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预约管理API接口
"""

from flask import Blueprint, request
from config.database import execute_query, execute_update, execute_paginated_query, execute_transaction
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response, conflict_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

# 创建蓝图
reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 100, 'default': 10},
    'laboratory_id': {'type': 'integer', 'min_value': 1},
    'user_id': {'type': 'integer', 'min_value': 1},
    'status': {'type': 'string', 'choices': ['pending', 'confirmed', 'cancelled', 'completed']},
    'date_from': {'type': 'string'},  # YYYY-MM-DD格式
    'date_to': {'type': 'string'},    # YYYY-MM-DD格式
    'search': {'type': 'string', 'max_length': 100}
})
def get_reservations():
    """获取预约列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['page_size']
        laboratory_id = params.get('laboratory_id')
        user_id = params.get('user_id')
        status = params.get('status')
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        search = params.get('search')
        
        # 非管理员只能查看自己的预约
        current_user = request.current_user
        if current_user['role'] not in ['admin', 'teacher']:
            user_id = current_user['id']
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        if laboratory_id:
            where_conditions.append('r.laboratory_id = %s')
            query_params.append(laboratory_id)
        
        if user_id:
            where_conditions.append('r.user_id = %s')
            query_params.append(user_id)
        
        if status:
            where_conditions.append('r.status = %s')
            query_params.append(status)
        
        if date_from:
            where_conditions.append('r.reservation_date >= %s')
            query_params.append(date_from)
        
        if date_to:
            where_conditions.append('r.reservation_date <= %s')
            query_params.append(date_to)
        
        if search:
            where_conditions.append('(r.purpose LIKE %s OR u.name LIKE %s OR l.name LIKE %s)')
            search_param = f'%{search}%'
            query_params.extend([search_param, search_param, search_param])
        
        # 构建SQL
        base_sql = """
        SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.purpose, 
               r.status, r.equipment_ids, r.created_at, r.updated_at,
               u.name as user_name, u.email as user_email,
               l.name as laboratory_name, l.location as laboratory_location
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN laboratories l ON r.laboratory_id = l.id
        """
        
        if where_conditions:
            base_sql += ' WHERE ' + ' AND '.join(where_conditions)
        
        base_sql += ' ORDER BY r.reservation_date DESC, r.start_time DESC'
        
        # 执行分页查询
        result = execute_paginated_query(base_sql, tuple(query_params), page, page_size)
        
        if not result['success']:
            logger.error(f"查询预约列表失败: {result.get('error')}")
            return error_response("获取预约列表失败")
        
        # 格式化数据
        reservations = []
        for reservation in result['data']:
            # 获取设备信息
            equipment_list = []
            if reservation['equipment_ids']:
                equipment_ids = reservation['equipment_ids'].split(',')
                if equipment_ids and equipment_ids[0]:  # 确保不是空字符串
                    equipment_sql = """
                    SELECT id, name, model
                    FROM equipment
                    WHERE id IN ({})
                    """.format(','.join(['%s'] * len(equipment_ids)))
                    
                    equipment_result = execute_query(equipment_sql, tuple(equipment_ids))
                    if equipment_result['success']:
                        for eq in equipment_result['data']:
                            equipment_list.append({
                                'id': eq['id'],
                                'name': eq['name'],
                                'model': eq['model']
                            })
            
            reservations.append({
                'id': reservation['id'],
                'reservation_date': reservation['reservation_date'].isoformat() if reservation['reservation_date'] else None,
                'start_time': str(reservation['start_time']) if reservation['start_time'] else None,
                'end_time': str(reservation['end_time']) if reservation['end_time'] else None,
                'purpose': reservation['purpose'],
                'status': reservation['status'],
                'equipment': equipment_list,
                'user': {
                    'name': reservation['user_name'],
                    'email': reservation['user_email']
                },
                'laboratory': {
                    'name': reservation['laboratory_name'],
                    'location': reservation['laboratory_location']
                },
                'created_at': reservation['created_at'].isoformat() if reservation['created_at'] else None,
                'updated_at': reservation['updated_at'].isoformat() if reservation['updated_at'] else None
            })
        
        return paginated_response(reservations, result['pagination'], "获取预约列表成功")
        
    except Exception as e:
        logger.error(f"获取预约列表接口错误: {str(e)}")
        return error_response("获取预约列表失败")

@reservations_bp.route('/<int:reservation_id>', methods=['GET'])
@require_auth
def get_reservation(reservation_id):
    """获取预约详情"""
    try:
        current_user = request.current_user
        
        # 构建查询条件
        where_condition = "r.id = %s"
        query_params = [reservation_id]
        
        # 非管理员只能查看自己的预约
        if current_user['role'] not in ['admin', 'teacher']:
            where_condition += " AND r.user_id = %s"
            query_params.append(current_user['id'])
        
        sql = f"""
        SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.purpose, 
               r.status, r.equipment_ids, r.created_at, r.updated_at,
               r.user_id, u.name as user_name, u.email as user_email,
               r.laboratory_id, l.name as laboratory_name, l.location as laboratory_location
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN laboratories l ON r.laboratory_id = l.id
        WHERE {where_condition}
        """
        
        result = execute_query(sql, tuple(query_params))
        
        if not result['success']:
            logger.error(f"查询预约详情失败: {result.get('error')}")
            return error_response("获取预约详情失败")
        
        if not result['data']:
            return not_found_response("预约不存在")
        
        reservation = result['data'][0]
        
        # 获取设备信息
        equipment_list = []
        if reservation['equipment_ids']:
            equipment_ids = reservation['equipment_ids'].split(',')
            if equipment_ids and equipment_ids[0]:  # 确保不是空字符串
                equipment_sql = """
                SELECT id, name, model, status
                FROM equipment
                WHERE id IN ({})
                """.format(','.join(['%s'] * len(equipment_ids)))
                
                equipment_result = execute_query(equipment_sql, tuple(equipment_ids))
                if equipment_result['success']:
                    for eq in equipment_result['data']:
                        equipment_list.append({
                            'id': eq['id'],
                            'name': eq['name'],
                            'model': eq['model'],
                            'status': eq['status']
                        })
        
        reservation_info = {
            'id': reservation['id'],
            'reservation_date': reservation['reservation_date'].isoformat() if reservation['reservation_date'] else None,
            'start_time': str(reservation['start_time']) if reservation['start_time'] else None,
            'end_time': str(reservation['end_time']) if reservation['end_time'] else None,
            'purpose': reservation['purpose'],
            'status': reservation['status'],
            'equipment': equipment_list,
            'user_id': reservation['user_id'],
            'user': {
                'name': reservation['user_name'],
                'email': reservation['user_email']
            },
            'laboratory_id': reservation['laboratory_id'],
            'laboratory': {
                'name': reservation['laboratory_name'],
                'location': reservation['laboratory_location']
            },
            'created_at': reservation['created_at'].isoformat() if reservation['created_at'] else None,
            'updated_at': reservation['updated_at'].isoformat() if reservation['updated_at'] else None
        }
        
        return success_response(reservation_info, "获取预约详情成功")
        
    except Exception as e:
        logger.error(f"获取预约详情接口错误: {str(e)}")
        return error_response("获取预约详情失败")

@reservations_bp.route('', methods=['POST'])
@require_auth
@validate_json_data({
    'laboratory_id': {'required': True, 'type': 'integer', 'min_value': 1},
    'reservation_date': {'required': True, 'type': 'date_string'},
    'start_time': {'required': True, 'type': 'string'},  # HH:MM格式
    'end_time': {'required': True, 'type': 'string'},    # HH:MM格式
    'purpose': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 500},
    'equipment_ids': {'required': False, 'type': 'list'}  # 设备ID列表
})
def create_reservation():
    """创建预约"""
    try:
        data = request.validated_data
        current_user = request.current_user
        
        laboratory_id = data['laboratory_id']
        reservation_date = data['reservation_date']
        start_time = data['start_time']
        end_time = data['end_time']
        purpose = data['purpose']
        equipment_ids = data.get('equipment_ids', [])
        
        # 验证时间格式和逻辑
        try:
            start_datetime = datetime.strptime(f"{reservation_date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{reservation_date} {end_time}", "%Y-%m-%d %H:%M")
            
            if start_datetime >= end_datetime:
                return error_response("结束时间必须晚于开始时间")
            
            if start_datetime <= datetime.now():
                return error_response("预约时间不能是过去的时间")
                
        except ValueError:
            return error_response("时间格式错误，请使用HH:MM格式")
        
        # 检查实验室是否存在且可用
        lab_check_sql = "SELECT id, name, status FROM laboratories WHERE id = %s"
        lab_result = execute_query(lab_check_sql, (laboratory_id,))
        
        if not lab_result['success']:
            return error_response("创建预约失败，请稍后重试")
        
        if not lab_result['data']:
            return error_response("指定的实验室不存在")
        
        lab = lab_result['data'][0]
        if lab['status'] != 'active':
            return error_response(f"实验室状态为{lab['status']}，无法预约")
        
        # 检查时间冲突
        conflict_sql = """
        SELECT id FROM reservations
        WHERE laboratory_id = %s 
        AND reservation_date = %s 
        AND status IN ('confirmed', 'pending')
        AND ((start_time <= %s AND end_time > %s) 
             OR (start_time < %s AND end_time >= %s) 
             OR (start_time >= %s AND end_time <= %s))
        """
        conflict_result = execute_query(conflict_sql, (
            laboratory_id, reservation_date, start_time, start_time,
            end_time, end_time, start_time, end_time
        ))
        
        if not conflict_result['success']:
            return error_response("创建预约失败，请稍后重试")
        
        if conflict_result['data']:
            return conflict_response("该时间段已被预约")
        
        # 验证设备
        equipment_ids_str = ""
        if equipment_ids:
            # 检查设备是否存在且属于该实验室
            equipment_check_sql = """
            SELECT id FROM equipment
            WHERE id IN ({}) AND laboratory_id = %s AND status = 'available'
            """.format(','.join(['%s'] * len(equipment_ids)))
            
            equipment_params = list(equipment_ids) + [laboratory_id]
            equipment_result = execute_query(equipment_check_sql, tuple(equipment_params))
            
            if not equipment_result['success']:
                return error_response("创建预约失败，请稍后重试")
            
            if len(equipment_result['data']) != len(equipment_ids):
                return error_response("部分设备不存在或不可用")
            
            equipment_ids_str = ','.join(map(str, equipment_ids))
        
        # 创建预约
        insert_sql = """
        INSERT INTO reservations (user_id, laboratory_id, reservation_date, start_time, 
                                end_time, purpose, equipment_ids, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        # 学生预约需要审核，教师和管理员直接确认
        status = 'confirmed' if current_user['role'] in ['admin', 'teacher'] else 'pending'
        
        insert_result = execute_update(insert_sql, (
            current_user['id'], laboratory_id, reservation_date, start_time,
            end_time, purpose, equipment_ids_str, status
        ))
        
        if not insert_result['success']:
            logger.error(f"创建预约失败: {insert_result.get('error')}")
            return error_response("创建预约失败，请稍后重试")
        
        # 获取新创建的预约信息
        reservation_id = insert_result['last_insert_id']
        reservation_sql = """
        SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.purpose, 
               r.status, r.equipment_ids, r.created_at,
               l.name as laboratory_name, l.location as laboratory_location
        FROM reservations r
        JOIN laboratories l ON r.laboratory_id = l.id
        WHERE r.id = %s
        """
        reservation_result = execute_query(reservation_sql, (reservation_id,))
        
        if reservation_result['success'] and reservation_result['data']:
            reservation = reservation_result['data'][0]
            
            # 获取设备信息
            equipment_list = []
            if reservation['equipment_ids']:
                equipment_ids_list = reservation['equipment_ids'].split(',')
                if equipment_ids_list and equipment_ids_list[0]:
                    equipment_sql = """
                    SELECT id, name, model
                    FROM equipment
                    WHERE id IN ({})
                    """.format(','.join(['%s'] * len(equipment_ids_list)))
                    
                    equipment_result = execute_query(equipment_sql, tuple(equipment_ids_list))
                    if equipment_result['success']:
                        for eq in equipment_result['data']:
                            equipment_list.append({
                                'id': eq['id'],
                                'name': eq['name'],
                                'model': eq['model']
                            })
            
            reservation_info = {
                'id': reservation['id'],
                'reservation_date': reservation['reservation_date'].isoformat() if reservation['reservation_date'] else None,
                'start_time': str(reservation['start_time']) if reservation['start_time'] else None,
                'end_time': str(reservation['end_time']) if reservation['end_time'] else None,
                'purpose': reservation['purpose'],
                'status': reservation['status'],
                'equipment': equipment_list,
                'laboratory': {
                    'name': reservation['laboratory_name'],
                    'location': reservation['laboratory_location']
                },
                'created_at': reservation['created_at'].isoformat() if reservation['created_at'] else None
            }
            
            message = "预约创建成功" if status == 'confirmed' else "预约创建成功，等待审核"
            return created_response(reservation_info, message)
        
        message = "预约创建成功" if status == 'confirmed' else "预约创建成功，等待审核"
        return created_response(None, message)
        
    except Exception as e:
        logger.error(f"创建预约接口错误: {str(e)}")
        return error_response("创建预约失败，请稍后重试")

@reservations_bp.route('/<int:reservation_id>', methods=['PUT'])
@require_auth
@validate_json_data({
    'reservation_date': {'required': False, 'type': 'date_string'},
    'start_time': {'required': False, 'type': 'string'},
    'end_time': {'required': False, 'type': 'string'},
    'purpose': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 500},
    'equipment_ids': {'required': False, 'type': 'list'},
    'status': {'required': False, 'type': 'string', 'choices': ['pending', 'confirmed', 'cancelled', 'completed']}
})
def update_reservation(reservation_id):
    """更新预约信息"""
    try:
        data = request.validated_data
        current_user = request.current_user
        
        # 检查预约是否存在
        check_sql = """
        SELECT id, user_id, laboratory_id, status, reservation_date, start_time, end_time
        FROM reservations 
        WHERE id = %s
        """
        check_result = execute_query(check_sql, (reservation_id,))
        
        if not check_result['success']:
            return error_response("更新失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("预约不存在")
        
        reservation = check_result['data'][0]
        
        # 权限检查：只有预约者本人或管理员/教师可以修改
        if (current_user['role'] not in ['admin', 'teacher'] and 
            current_user['id'] != reservation['user_id']):
            return error_response("没有权限修改此预约")
        
        # 已完成或已取消的预约不能修改
        if reservation['status'] in ['completed', 'cancelled']:
            return error_response("已完成或已取消的预约不能修改")
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        # 时间相关字段需要一起验证
        new_date = data.get('reservation_date', reservation['reservation_date'])
        new_start = data.get('start_time', str(reservation['start_time']))
        new_end = data.get('end_time', str(reservation['end_time']))
        
        # 验证时间逻辑
        if 'reservation_date' in data or 'start_time' in data or 'end_time' in data:
            try:
                start_datetime = datetime.strptime(f"{new_date} {new_start}", "%Y-%m-%d %H:%M")
                end_datetime = datetime.strptime(f"{new_date} {new_end}", "%Y-%m-%d %H:%M")
                
                if start_datetime >= end_datetime:
                    return error_response("结束时间必须晚于开始时间")
                
                if start_datetime <= datetime.now():
                    return error_response("预约时间不能是过去的时间")
                    
            except ValueError:
                return error_response("时间格式错误")
            
            # 检查时间冲突（排除当前预约）
            conflict_sql = """
            SELECT id FROM reservations
            WHERE laboratory_id = %s 
            AND reservation_date = %s 
            AND status IN ('confirmed', 'pending')
            AND id != %s
            AND ((start_time <= %s AND end_time > %s) 
                 OR (start_time < %s AND end_time >= %s) 
                 OR (start_time >= %s AND end_time <= %s))
            """
            conflict_result = execute_query(conflict_sql, (
                reservation['laboratory_id'], new_date, reservation_id,
                new_start, new_start, new_end, new_end, new_start, new_end
            ))
            
            if not conflict_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if conflict_result['data']:
                return conflict_response("该时间段已被预约")
        
        if 'reservation_date' in data:
            update_fields.append('reservation_date = %s')
            update_values.append(data['reservation_date'])
        
        if 'start_time' in data:
            update_fields.append('start_time = %s')
            update_values.append(data['start_time'])
        
        if 'end_time' in data:
            update_fields.append('end_time = %s')
            update_values.append(data['end_time'])
        
        if 'purpose' in data:
            update_fields.append('purpose = %s')
            update_values.append(data['purpose'])
        
        if 'equipment_ids' in data:
            equipment_ids = data['equipment_ids']
            equipment_ids_str = ""
            
            if equipment_ids:
                # 验证设备
                equipment_check_sql = """
                SELECT id FROM equipment
                WHERE id IN ({}) AND laboratory_id = %s AND status = 'available'
                """.format(','.join(['%s'] * len(equipment_ids)))
                
                equipment_params = list(equipment_ids) + [reservation['laboratory_id']]
                equipment_result = execute_query(equipment_check_sql, tuple(equipment_params))
                
                if not equipment_result['success']:
                    return error_response("更新失败，请稍后重试")
                
                if len(equipment_result['data']) != len(equipment_ids):
                    return error_response("部分设备不存在或不可用")
                
                equipment_ids_str = ','.join(map(str, equipment_ids))
            
            update_fields.append('equipment_ids = %s')
            update_values.append(equipment_ids_str)
        
        if 'status' in data:
            # 只有管理员和教师可以修改状态
            if current_user['role'] not in ['admin', 'teacher']:
                return error_response("没有权限修改预约状态")
            
            update_fields.append('status = %s')
            update_values.append(data['status'])
        
        if not update_fields:
            return error_response("没有需要更新的字段")
        
        # 添加更新时间
        update_fields.append('updated_at = NOW()')
        update_values.append(reservation_id)
        
        # 执行更新
        update_sql = f"UPDATE reservations SET {', '.join(update_fields)} WHERE id = %s"
        update_result = execute_update(update_sql, tuple(update_values))
        
        if not update_result['success']:
            logger.error(f"更新预约信息失败: {update_result.get('error')}")
            return error_response("更新失败，请稍后重试")
        
        return updated_response(None, "预约信息更新成功")
        
    except Exception as e:
        logger.error(f"更新预约信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@reservations_bp.route('/<int:reservation_id>', methods=['DELETE'])
@require_auth
def delete_reservation(reservation_id):
    """删除/取消预约"""
    try:
        current_user = request.current_user
        
        # 检查预约是否存在
        check_sql = """
        SELECT id, user_id, status, reservation_date, start_time
        FROM reservations 
        WHERE id = %s
        """
        check_result = execute_query(check_sql, (reservation_id,))
        
        if not check_result['success']:
            return error_response("操作失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("预约不存在")
        
        reservation = check_result['data'][0]
        
        # 权限检查：只有预约者本人或管理员可以删除
        if (current_user['role'] != 'admin' and 
            current_user['id'] != reservation['user_id']):
            return error_response("没有权限删除此预约")
        
        # 已完成的预约不能删除
        if reservation['status'] == 'completed':
            return error_response("已完成的预约不能删除")
        
        # 检查是否是过去的预约
        reservation_datetime = datetime.combine(
            reservation['reservation_date'], 
            reservation['start_time']
        )
        
        if reservation_datetime <= datetime.now():
            # 过去的预约标记为取消而不是删除
            cancel_sql = "UPDATE reservations SET status = 'cancelled', updated_at = NOW() WHERE id = %s"
            cancel_result = execute_update(cancel_sql, (reservation_id,))
            
            if not cancel_result['success']:
                logger.error(f"取消预约失败: {cancel_result.get('error')}")
                return error_response("取消预约失败，请稍后重试")
            
            return updated_response(None, "预约已取消")
        else:
            # 未来的预约可以直接删除
            delete_sql = "DELETE FROM reservations WHERE id = %s"
            delete_result = execute_update(delete_sql, (reservation_id,))
            
            if not delete_result['success']:
                logger.error(f"删除预约失败: {delete_result.get('error')}")
                return error_response("删除预约失败，请稍后重试")
            
            return deleted_response("预约删除成功")
        
    except Exception as e:
        logger.error(f"删除预约接口错误: {str(e)}")
        return error_response("操作失败，请稍后重试")

@reservations_bp.route('/statistics', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_query_params({
    'date_from': {'type': 'string'},  # YYYY-MM-DD格式
    'date_to': {'type': 'string'},    # YYYY-MM-DD格式
    'laboratory_id': {'type': 'integer', 'min_value': 1}
})
def get_reservation_statistics():
    """获取预约统计信息"""
    try:
        params = request.validated_params
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        laboratory_id = params.get('laboratory_id')
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        if date_from:
            where_conditions.append('reservation_date >= %s')
            query_params.append(date_from)
        
        if date_to:
            where_conditions.append('reservation_date <= %s')
            query_params.append(date_to)
        
        if laboratory_id:
            where_conditions.append('laboratory_id = %s')
            query_params.append(laboratory_id)
        
        where_clause = ' WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # 按状态统计
        status_sql = f"""
        SELECT status, COUNT(*) as count
        FROM reservations
        {where_clause}
        GROUP BY status
        """
        status_result = execute_query(status_sql, tuple(query_params))
        
        status_stats = {}
        total_count = 0
        if status_result['success']:
            for row in status_result['data']:
                status_stats[row['status']] = row['count']
                total_count += row['count']
        
        # 按实验室统计
        lab_sql = f"""
        SELECT l.name as laboratory_name, COUNT(r.id) as count
        FROM laboratories l
        LEFT JOIN reservations r ON l.id = r.laboratory_id
        {where_clause.replace('laboratory_id', 'r.laboratory_id') if where_clause else ''}
        GROUP BY l.id, l.name
        ORDER BY count DESC
        """
        lab_result = execute_query(lab_sql, tuple(query_params))
        
        lab_stats = []
        if lab_result['success']:
            for row in lab_result['data']:
                lab_stats.append({
                    'laboratory_name': row['laboratory_name'],
                    'reservation_count': row['count']
                })
        
        # 按用户统计（前10名）
        user_sql = f"""
        SELECT u.name as user_name, COUNT(r.id) as count
        FROM users u
        JOIN reservations r ON u.id = r.user_id
        {where_clause}
        GROUP BY u.id, u.name
        ORDER BY count DESC
        LIMIT 10
        """
        user_result = execute_query(user_sql, tuple(query_params))
        
        user_stats = []
        if user_result['success']:
            for row in user_result['data']:
                user_stats.append({
                    'user_name': row['user_name'],
                    'reservation_count': row['count']
                })
        
        # 按日期统计（最近30天）
        daily_sql = f"""
        SELECT reservation_date, COUNT(*) as count
        FROM reservations
        WHERE reservation_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        {' AND ' + ' AND '.join(where_conditions) if where_conditions else ''}
        GROUP BY reservation_date
        ORDER BY reservation_date ASC
        """
        daily_result = execute_query(daily_sql, tuple(query_params))
        
        daily_stats = []
        if daily_result['success']:
            for row in daily_result['data']:
                daily_stats.append({
                    'date': row['reservation_date'].isoformat() if row['reservation_date'] else None,
                    'count': row['count']
                })
        
        statistics = {
            'total_reservations': total_count,
            'status_distribution': status_stats,
            'laboratory_distribution': lab_stats,
            'top_users': user_stats,
            'daily_trend': daily_stats
        }
        
        return success_response(statistics, "获取预约统计信息成功")
        
    except Exception as e:
        logger.error(f"获取预约统计信息接口错误: {str(e)}")
        return error_response("获取统计信息失败")