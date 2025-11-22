#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验室管理API接口
"""

from flask import Blueprint, request
from backend.init_database import execute_query, execute_update, execute_paginated_query
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response, conflict_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
laboratories_bp = Blueprint('laboratories', __name__)

@laboratories_bp.route('', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'status': {'type': 'string', 'choices': ['available', 'maintenance', 'occupied']},
    'search': {'type': 'string', 'max_length': 100}
})
def get_laboratories():
    """获取实验室列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['page_size']
        status = params.get('status')
        search = params.get('search')
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        if status:
            where_conditions.append('status = %s')
            query_params.append(status)
        
        if search:
            where_conditions.append('(name LIKE %s OR location LIKE %s OR description LIKE %s)')
            search_param = f'%{search}%'
            query_params.extend([search_param, search_param, search_param])
        
        # 构建SQL（兼容未添加 manager_id 字段的旧库）
        has_manager_col = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='laboratories' AND COLUMN_NAME='manager_id' LIMIT 1"
        )
        join_manager = has_manager_col.get('success') and bool(has_manager_col.get('data'))
        if join_manager:
            base_sql = (
                "SELECT l.id, l.name, l.location, l.capacity, l.description, l.status, "
                "       l.created_at, l.updated_at, l.manager_id, u.name AS manager_name "
                "FROM laboratories l LEFT JOIN users u ON l.manager_id = u.id"
            )
        else:
            base_sql = (
                "SELECT id, name, location, capacity, description, status, created_at, updated_at "
                "FROM laboratories"
            )
        
        if where_conditions:
            base_sql += ' WHERE ' + ' AND '.join(where_conditions)
        
        base_sql += (' ORDER BY l.name ASC' if join_manager else ' ORDER BY name ASC')
        
        # 执行分页查询
        result = execute_paginated_query(base_sql, tuple(query_params), page, page_size)
        
        if not result['success']:
            logger.error(f"查询实验室列表失败: {result.get('error')}")
            return error_response("获取实验室列表失败")
        
        # 格式化数据
        laboratories = []
        for lab in result['data']:
            laboratories.append({
                'id': lab['id'],
                'name': lab['name'],
                'location': lab['location'],
                'capacity': lab['capacity'],
                'description': lab['description'],
                'status': lab['status'],
                'manager_id': lab.get('manager_id') if join_manager else None,
                'manager_name': lab.get('manager_name') if join_manager else None,
                'created_at': lab['created_at'].isoformat() if lab['created_at'] else None,
                'updated_at': lab['updated_at'].isoformat() if lab['updated_at'] else None
            })
        
        return paginated_response(laboratories, result['pagination'], "获取实验室列表成功")
        
    except Exception as e:
        logger.error(f"获取实验室列表接口错误: {str(e)}")
        return error_response("获取实验室列表失败")

@laboratories_bp.route('/<int:lab_id>', methods=['GET'])
@require_auth
def get_laboratory(lab_id):
    """获取实验室详情"""
    try:
        # 兼容未添加 manager_id 字段的旧库
        has_manager_col = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='laboratories' AND COLUMN_NAME='manager_id' LIMIT 1"
        )
        join_manager = has_manager_col.get('success') and bool(has_manager_col.get('data'))
        if join_manager:
            sql = (
                "SELECT l.id, l.name, l.location, l.capacity, l.description, l.status, "
                "       l.created_at, l.updated_at, l.manager_id, u.name AS manager_name "
                "FROM laboratories l LEFT JOIN users u ON l.manager_id = u.id WHERE l.id = %s"
            )
        else:
            sql = (
                "SELECT id, name, location, capacity, description, status, created_at, updated_at "
                "FROM laboratories WHERE id = %s"
            )
        result = execute_query(sql, (lab_id,))
        
        if not result['success']:
            logger.error(f"查询实验室详情失败: {result.get('error')}")
            return error_response("获取实验室详情失败")
        
        if not result['data']:
            return not_found_response("实验室不存在")
        
        lab = result['data'][0]
        lab_info = {
            'id': lab['id'],
            'name': lab['name'],
            'location': lab['location'],
            'capacity': lab['capacity'],
            'description': lab['description'],
            'status': lab['status'],
            'manager_id': lab.get('manager_id') if join_manager else None,
            'manager_name': lab.get('manager_name') if join_manager else None,
            'created_at': lab['created_at'].isoformat() if lab['created_at'] else None,
            'updated_at': lab['updated_at'].isoformat() if lab['updated_at'] else None
        }
        
        # 获取实验室设备信息
        equipment_sql = """
        SELECT id, name, model, status
        FROM equipment 
        WHERE laboratory_id = %s
        ORDER BY name ASC
        """
        equipment_result = execute_query(equipment_sql, (lab_id,))
        
        if equipment_result['success']:
            equipment_list = []
            for eq in equipment_result['data']:
                equipment_list.append({
                    'id': eq['id'],
                    'name': eq['name'],
                    'model': eq['model'],
                    'status': eq['status']
                })
            lab_info['equipment'] = equipment_list
        else:
            lab_info['equipment'] = []
        
        return success_response(lab_info, "获取实验室详情成功")
        
    except Exception as e:
        logger.error(f"获取实验室详情接口错误: {str(e)}")
        return error_response("获取实验室详情失败")

@laboratories_bp.route('/<int:lab_id>/equipment', methods=['GET'])
@require_auth
def get_laboratory_equipment(lab_id):
    """获取指定实验室的设备列表（兼容前端 /labs/{id}/equipment 路径）"""
    try:
        # 验证实验室是否存在
        lab_check = execute_query("SELECT id FROM laboratories WHERE id = %s", (lab_id,))
        if not lab_check['success']:
            return error_response("查询失败，请稍后重试")
        if not lab_check['data']:
            return not_found_response("实验室不存在")

        eq_sql = (
            "SELECT id, name, model, serial_number, status, purchase_date, warranty_date, created_at, updated_at "
            "FROM equipment WHERE laboratory_id = %s ORDER BY name ASC"
        )
        eq_res = execute_query(eq_sql, (lab_id,))

        if not eq_res['success']:
            logger.error(f"查询实验室设备失败: {eq_res.get('error')}")
            return error_response("获取设备列表失败")

        equipment = []
        for e in eq_res['data']:
            equipment.append({
                'id': e['id'],
                'name': e['name'],
                'model': e['model'],
                'serial_number': e['serial_number'],
                'status': e['status'],
                'purchase_date': e['purchase_date'].isoformat() if e.get('purchase_date') else None,
                'warranty_date': e['warranty_date'].isoformat() if e.get('warranty_date') else None,
                'created_at': e['created_at'].isoformat() if e.get('created_at') else None,
                'updated_at': e['updated_at'].isoformat() if e.get('updated_at') else None,
            })

        return success_response(equipment, "获取设备列表成功")
    except Exception as e:
        logger.error(f"获取实验室设备接口错误: {str(e)}")
        return error_response("获取设备列表失败")

@laboratories_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'location': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 200},
    'capacity': {'required': True, 'type': 'integer', 'min_value': 1, 'max_value': 1000},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'status': {'required': False, 'type': 'string', 'choices': ['available', 'maintenance', 'occupied']},
    'manager_id': {'required': False, 'type': 'integer', 'min_value': 1}
})
def create_laboratory():
    """创建实验室"""
    try:
        data = request.validated_data
        name = data['name']
        location = data['location']
        capacity = data['capacity']
        description = data.get('description', '')
        status = data.get('status', 'available')
        manager_id = data.get('manager_id')
        
        # 检查实验室名称是否已存在
        check_sql = "SELECT id FROM laboratories WHERE name = %s"
        check_result = execute_query(check_sql, (name,))
        
        if not check_result['success']:
            logger.error(f"检查实验室名称失败: {check_result.get('error')}")
            return error_response("创建实验室失败，请稍后重试")
        
        if check_result['data']:
            return conflict_response("实验室名称已存在")
        
        # 验证负责人用户是否存在（若提供）
        if manager_id:
            user_check = execute_query("SELECT id FROM users WHERE id = %s", (manager_id,))
            if not (user_check['success'] and user_check['data']):
                return not_found_response("负责人用户不存在")

        # 插入新实验室（兼容无 manager_id 列的旧库）
        has_manager_col = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='laboratories' AND COLUMN_NAME='manager_id' LIMIT 1"
        )
        can_set_manager = has_manager_col.get('success') and bool(has_manager_col.get('data'))
        if can_set_manager:
            insert_sql = (
                "INSERT INTO laboratories (name, location, capacity, description, status, manager_id, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW())"
            )
            insert_result = execute_update(insert_sql, (name, location, capacity, description, status, manager_id))
        else:
            insert_sql = (
                "INSERT INTO laboratories (name, location, capacity, description, status, created_at) "
                "VALUES (%s, %s, %s, %s, %s, NOW())"
            )
            insert_result = execute_update(insert_sql, (name, location, capacity, description, status))
        
        if not insert_result['success']:
            logger.error(f"创建实验室失败: {insert_result.get('error')}")
            return error_response("创建实验室失败，请稍后重试")
        
        # 获取新创建的实验室信息
        lab_id = insert_result['last_insert_id']
        # 再次确保负责人已写入（处理部分环境中 INSERT 未写入的情况）
        if can_set_manager and manager_id:
            _upd = execute_update("UPDATE laboratories SET manager_id = %s, updated_at = NOW() WHERE id = %s", (manager_id, lab_id))
        # 返回创建后的实验室信息（含负责人名称，若支持）
        if can_set_manager:
            lab_sql = (
                "SELECT l.id, l.name, l.location, l.capacity, l.description, l.status, l.created_at, l.manager_id, u.name AS manager_name "
                "FROM laboratories l LEFT JOIN users u ON l.manager_id = u.id WHERE l.id = %s"
            )
        else:
            lab_sql = (
                "SELECT id, name, location, capacity, description, status, created_at FROM laboratories WHERE id = %s"
            )
        lab_result = execute_query(lab_sql, (lab_id,))
        
        if lab_result['success'] and lab_result['data']:
            lab = lab_result['data'][0]
            lab_info = {
                'id': lab['id'],
                'name': lab['name'],
                'location': lab['location'],
                'capacity': lab['capacity'],
                'description': lab['description'],
                'status': lab['status'],
                'manager_id': lab.get('manager_id'),
                'manager_name': lab.get('manager_name'),
                'created_at': lab['created_at'].isoformat() if lab['created_at'] else None
            }
            
            return created_response(lab_info, "实验室创建成功")
        
        return created_response(None, "实验室创建成功")
        
    except Exception as e:
        logger.error(f"创建实验室接口错误: {str(e)}")
        return error_response("创建实验室失败，请稍后重试")

@laboratories_bp.route('/<int:lab_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'location': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 200},
    'capacity': {'required': False, 'type': 'integer', 'min_value': 1, 'max_value': 1000},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'status': {'required': False, 'type': 'string', 'choices': ['available', 'maintenance', 'occupied']},
    'manager_id': {'required': False, 'type': 'integer', 'min_value': 1}
})
def update_laboratory(lab_id):
    """更新实验室信息"""
    try:
        data = request.validated_data
        
        # 检查实验室是否存在
        check_sql = "SELECT id FROM laboratories WHERE id = %s"
        check_result = execute_query(check_sql, (lab_id,))
        
        if not check_result['success']:
            return error_response("更新失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("实验室不存在")
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        if 'name' in data and data['name'] is not None:
            # 检查名称是否已被其他实验室使用
            name_check_sql = "SELECT id FROM laboratories WHERE name = %s AND id != %s"
            name_check_result = execute_query(name_check_sql, (data['name'], lab_id))
            
            if not name_check_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if name_check_result['data']:
                return conflict_response("实验室名称已被使用")
            
            update_fields.append('name = %s')
            update_values.append(data['name'])
        
        if 'location' in data and data['location'] is not None:
            update_fields.append('location = %s')
            update_values.append(data['location'])
        
        if 'capacity' in data and data['capacity'] is not None:
            update_fields.append('capacity = %s')
            update_values.append(data['capacity'])
        
        if 'description' in data and data['description'] is not None:
            update_fields.append('description = %s')
            update_values.append(data['description'])
        
        if 'status' in data and data['status'] is not None:
            update_fields.append('status = %s')
            update_values.append(data['status'])

        # 更新负责人（若提供且列存在）
        if 'manager_id' in data:
            manager_id = data.get('manager_id')
            # 验证用户存在
            if manager_id is not None:
                user_check = execute_query("SELECT id FROM users WHERE id = %s", (manager_id,))
                if not (user_check['success'] and user_check['data']):
                    return not_found_response("负责人用户不存在")
            # 检查列存在
            has_manager_col = execute_query(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='laboratories' AND COLUMN_NAME='manager_id' LIMIT 1"
            )
            if has_manager_col.get('success') and has_manager_col.get('data'):
                update_fields.append('manager_id = %s')
                update_values.append(manager_id)
        
        if not update_fields:
            return error_response("没有需要更新的字段")
        
        # 添加更新时间
        update_fields.append('updated_at = NOW()')
        update_values.append(lab_id)
        
        # 执行更新
        update_sql = f"UPDATE laboratories SET {', '.join(update_fields)} WHERE id = %s"
        update_result = execute_update(update_sql, tuple(update_values))
        
        if not update_result['success']:
            logger.error(f"更新实验室信息失败: {update_result.get('error')}")
            return error_response("更新失败，请稍后重试")
        
        # 获取更新后的实验室信息
        # 返回更新后的信息（含负责人名称，若支持）
        has_manager_col = execute_query(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='laboratories' AND COLUMN_NAME='manager_id' LIMIT 1"
        )
        join_manager = has_manager_col.get('success') and bool(has_manager_col.get('data'))
        if join_manager:
            lab_sql = (
                "SELECT l.id, l.name, l.location, l.capacity, l.description, l.status, l.created_at, l.updated_at, l.manager_id, u.name AS manager_name "
                "FROM laboratories l LEFT JOIN users u ON l.manager_id = u.id WHERE l.id = %s"
            )
        else:
            lab_sql = (
                "SELECT id, name, location, capacity, description, status, created_at, updated_at FROM laboratories WHERE id = %s"
            )
        lab_result = execute_query(lab_sql, (lab_id,))
        
        if lab_result['success'] and lab_result['data']:
            lab = lab_result['data'][0]
            lab_info = {
                'id': lab['id'],
                'name': lab['name'],
                'location': lab['location'],
                'capacity': lab['capacity'],
                'description': lab['description'],
                'status': lab['status'],
                'manager_id': lab.get('manager_id'),
                'manager_name': lab.get('manager_name'),
                'created_at': lab['created_at'].isoformat() if lab['created_at'] else None,
                'updated_at': lab['updated_at'].isoformat() if lab['updated_at'] else None
            }
            
            return updated_response(lab_info, "实验室信息更新成功")
        
        return updated_response(None, "实验室信息更新成功")
        
    except Exception as e:
        logger.error(f"更新实验室信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@laboratories_bp.route('/<int:lab_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_laboratory(lab_id):
    """删除实验室"""
    try:
        # 检查实验室是否存在
        check_sql = "SELECT id, name FROM laboratories WHERE id = %s"
        check_result = execute_query(check_sql, (lab_id,))
        
        if not check_result['success']:
            return error_response("删除失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("实验室不存在")
        
        # 检查实验室是否有相关的设备
        equipment_check_sql = "SELECT COUNT(*) as count FROM equipment WHERE laboratory_id = %s"
        equipment_result = execute_query(equipment_check_sql, (lab_id,))
        
        if equipment_result['success'] and equipment_result['data']:
            equipment_count = equipment_result['data'][0]['count']
            if equipment_count > 0:
                return error_response("该实验室有相关设备，请先删除设备")
        
        # 检查实验室是否有相关的预约记录
        reservation_check_sql = "SELECT COUNT(*) as count FROM reservations WHERE laboratory_id = %s"
        reservation_result = execute_query(reservation_check_sql, (lab_id,))
        
        if reservation_result['success'] and reservation_result['data']:
            reservation_count = reservation_result['data'][0]['count']
            if reservation_count > 0:
                return error_response("该实验室有相关的预约记录，无法删除")
        
        # 删除实验室
        delete_sql = "DELETE FROM laboratories WHERE id = %s"
        delete_result = execute_update(delete_sql, (lab_id,))
        
        if not delete_result['success']:
            logger.error(f"删除实验室失败: {delete_result.get('error')}")
            return error_response("删除失败，请稍后重试")
        
        return deleted_response("实验室删除成功")
        
    except Exception as e:
        logger.error(f"删除实验室接口错误: {str(e)}")
        return error_response("删除失败，请稍后重试")

@laboratories_bp.route('/<int:lab_id>/availability', methods=['GET'])
@require_auth
@validate_query_params({
    'date': {'required': True, 'type': 'string'},  # YYYY-MM-DD格式
    'start_time': {'type': 'string'},  # HH:MM格式
    'end_time': {'type': 'string'}     # HH:MM格式
})
def check_laboratory_availability(lab_id):
    """检查实验室可用性"""
    try:
        params = request.validated_params
        date = params['date']
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        
        # 检查实验室是否存在
        lab_check_sql = "SELECT id, name, status FROM laboratories WHERE id = %s"
        lab_result = execute_query(lab_check_sql, (lab_id,))
        
        if not lab_result['success']:
            return error_response("查询失败，请稍后重试")
        
        if not lab_result['data']:
            return not_found_response("实验室不存在")
        
        lab = lab_result['data'][0]
        
        # 如果实验室状态不可用，直接返回
        if lab['status'] != 'available':
            return success_response({
                'available': False,
                'reason': f"实验室状态为: {lab['status']}",
                'conflicting_reservations': []
            }, "实验室可用性查询成功")
        
        # 构建查询条件
        where_conditions = ["laboratory_id = %s", "reservation_date = %s", "status IN ('confirmed', 'pending')"]
        query_params = [lab_id, date]
        
        if start_time and end_time:
            # 检查时间冲突
            where_conditions.append("((start_time <= %s AND end_time > %s) OR (start_time < %s AND end_time >= %s) OR (start_time >= %s AND end_time <= %s))")
            query_params.extend([start_time, start_time, end_time, end_time, start_time, end_time])
        
        # 查询冲突的预约
        conflict_sql = f"""
        SELECT r.id, r.start_time, r.end_time, r.purpose, u.name as user_name
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        WHERE {' AND '.join(where_conditions)}
        ORDER BY r.start_time ASC
        """
        
        conflict_result = execute_query(conflict_sql, tuple(query_params))
        
        if not conflict_result['success']:
            logger.error(f"查询预约冲突失败: {conflict_result.get('error')}")
            return error_response("查询失败，请稍后重试")
        
        conflicting_reservations = []
        for reservation in conflict_result['data']:
            conflicting_reservations.append({
                'id': reservation['id'],
                'start_time': str(reservation['start_time']),
                'end_time': str(reservation['end_time']),
                'purpose': reservation['purpose'],
                'user_name': reservation['user_name']
            })
        
        available = len(conflicting_reservations) == 0
        
        return success_response({
            'available': available,
            'reason': "时间冲突" if not available else None,
            'conflicting_reservations': conflicting_reservations
        }, "实验室可用性查询成功")
        
    except Exception as e:
        logger.error(f"检查实验室可用性接口错误: {str(e)}")
        return error_response("查询失败，请稍后重试")