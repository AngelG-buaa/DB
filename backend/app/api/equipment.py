#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理API接口
"""

from flask import Blueprint, request
from config.database import execute_query, execute_update, execute_paginated_query
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response, conflict_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'laboratory_id': {'type': 'integer', 'min_value': 1},
    'status': {'type': 'string', 'choices': ['available', 'maintenance', 'damaged', 'retired']},
    'search': {'type': 'string', 'max_length': 100}
})
def get_equipment():
    """获取设备列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['page_size']
        laboratory_id = params.get('laboratory_id')
        status = params.get('status')
        search = params.get('search')
        
        # 构建查询条件
        where_conditions = []
        query_params = []
        
        if laboratory_id:
            where_conditions.append('e.laboratory_id = %s')
            query_params.append(laboratory_id)
        
        if status:
            where_conditions.append('e.status = %s')
            query_params.append(status)
        
        if search:
            where_conditions.append('(e.name LIKE %s OR e.model LIKE %s OR e.serial_number LIKE %s OR e.description LIKE %s)')
            search_param = f'%{search}%'
            query_params.extend([search_param, search_param, search_param, search_param])
        
        # 构建SQL
        base_sql = """
        SELECT e.id, e.name, e.model, e.serial_number, e.description, e.status, 
               e.purchase_date, e.warranty_date, e.created_at, e.updated_at,
               l.name as laboratory_name, l.location as laboratory_location
        FROM equipment e
        LEFT JOIN laboratories l ON e.laboratory_id = l.id
        """
        
        if where_conditions:
            base_sql += ' WHERE ' + ' AND '.join(where_conditions)
        
        base_sql += ' ORDER BY e.name ASC'
        
        # 执行分页查询
        result = execute_paginated_query(base_sql, tuple(query_params), page, page_size)
        
        if not result['success']:
            logger.error(f"查询设备列表失败: {result.get('error')}")
            return error_response("获取设备列表失败")
        
        # 格式化数据
        equipment_list = []
        for eq in result['data']:
            equipment_list.append({
                'id': eq['id'],
                'name': eq['name'],
                'model': eq['model'],
                'serial_number': eq['serial_number'],
                'description': eq['description'],
                'status': eq['status'],
                'purchase_date': eq['purchase_date'].isoformat() if eq['purchase_date'] else None,
                'warranty_date': eq['warranty_date'].isoformat() if eq['warranty_date'] else None,
                'laboratory': {
                    'name': eq['laboratory_name'],
                    'location': eq['laboratory_location']
                } if eq['laboratory_name'] else None,
                'created_at': eq['created_at'].isoformat() if eq['created_at'] else None,
                'updated_at': eq['updated_at'].isoformat() if eq['updated_at'] else None
            })
        
        return paginated_response(equipment_list, result['pagination'], "获取设备列表成功")
        
    except Exception as e:
        logger.error(f"获取设备列表接口错误: {str(e)}")
        return error_response("获取设备列表失败")

@equipment_bp.route('/<int:equipment_id>', methods=['GET'])
@require_auth
def get_equipment_detail(equipment_id):
    """获取设备详情"""
    try:
        sql = """
        SELECT e.id, e.name, e.model, e.serial_number, e.description, e.status, 
               e.purchase_date, e.warranty_date, e.created_at, e.updated_at,
               e.laboratory_id, l.name as laboratory_name, l.location as laboratory_location
        FROM equipment e
        LEFT JOIN laboratories l ON e.laboratory_id = l.id
        WHERE e.id = %s
        """
        result = execute_query(sql, (equipment_id,))
        
        if not result['success']:
            logger.error(f"查询设备详情失败: {result.get('error')}")
            return error_response("获取设备详情失败")
        
        if not result['data']:
            return not_found_response("设备不存在")
        
        eq = result['data'][0]
        equipment_info = {
            'id': eq['id'],
            'name': eq['name'],
            'model': eq['model'],
            'serial_number': eq['serial_number'],
            'description': eq['description'],
            'status': eq['status'],
            'purchase_date': eq['purchase_date'].isoformat() if eq['purchase_date'] else None,
            'warranty_date': eq['warranty_date'].isoformat() if eq['warranty_date'] else None,
            'laboratory_id': eq['laboratory_id'],
            'laboratory': {
                'name': eq['laboratory_name'],
                'location': eq['laboratory_location']
            } if eq['laboratory_name'] else None,
            'created_at': eq['created_at'].isoformat() if eq['created_at'] else None,
            'updated_at': eq['updated_at'].isoformat() if eq['updated_at'] else None
        }
        
        return success_response(equipment_info, "获取设备详情成功")
        
    except Exception as e:
        logger.error(f"获取设备详情接口错误: {str(e)}")
        return error_response("获取设备详情失败")

@equipment_bp.route('/<int:equipment_id>/maintenance', methods=['GET'])
@require_auth
def get_equipment_maintenance_list(equipment_id):
    """获取指定设备的维修记录列表（简版，无分页）"""
    try:
        sql = (
            "SELECT r.id, r.equipment_id, r.repair_person, r.fault_description, r.repair_description, "
            "r.repair_cost, r.repair_status, r.start_time, r.finish_time, r.expected_finish_date, r.remarks, "
            "r.repair_type, r.created_at, r.updated_at "
            "FROM equipment_repair r WHERE r.equipment_id = %s ORDER BY r.start_time DESC, r.id DESC"
        )
        result = execute_query(sql, (equipment_id,))
        if not result['success']:
            return error_response('获取设备维修记录失败')

        def _to_date(v):
            if not v:
                return None
            return v.date().isoformat() if hasattr(v, 'date') else str(v)[:10]

        def _map(row):
            status = row.get('repair_status')
            if status == 'reported':
                status = 'in_progress'
            return {
                'id': row.get('id'),
                'equipment_id': row.get('equipment_id'),
                'type': row.get('repair_type') or 'repair',
                'description': row.get('fault_description') or '',
                'technician': row.get('repair_person') or '',
                'cost': float(row.get('repair_cost') or 0),
                'start_date': _to_date(row.get('start_time')),
                'expected_completion_date': _to_date(row.get('expected_finish_date')),
                'actual_completion_date': _to_date(row.get('finish_time')),
                'status': status,
                'remarks': row.get('remarks') or row.get('repair_description') or '',
                'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
                'updated_at': row.get('updated_at').isoformat() if row.get('updated_at') else None,
            }

        records = [_map(row) for row in (result['data'] or [])]
        return success_response(records, '获取设备维修记录成功')
    except Exception as e:
        logger.error(f"获取设备维修记录接口错误: {str(e)}")
        return error_response('获取设备维修记录失败')

@equipment_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'model': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'serial_number': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'laboratory_id': {'required': True, 'type': 'integer', 'min_value': 1},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'status': {'required': False, 'type': 'string', 'choices': ['available', 'maintenance', 'damaged', 'retired']},
    'purchase_date': {'required': False, 'type': 'date_string'},
    'warranty_date': {'required': False, 'type': 'date_string'}
})
def create_equipment():
    """创建设备"""
    try:
        data = request.validated_data
        name = data['name']
        model = data['model']
        serial_number = data['serial_number']
        laboratory_id = data['laboratory_id']
        description = data.get('description', '')
        status = data.get('status', 'available')
        purchase_date = data.get('purchase_date')
        warranty_date = data.get('warranty_date')
        
        # 检查实验室是否存在
        lab_check_sql = "SELECT id FROM laboratories WHERE id = %s"
        lab_result = execute_query(lab_check_sql, (laboratory_id,))
        
        if not lab_result['success']:
            return error_response("创建设备失败，请稍后重试")
        
        if not lab_result['data']:
            return error_response("指定的实验室不存在")
        
        # 检查序列号是否已存在
        serial_check_sql = "SELECT id FROM equipment WHERE serial_number = %s"
        serial_result = execute_query(serial_check_sql, (serial_number,))
        
        if not serial_result['success']:
            return error_response("创建设备失败，请稍后重试")
        
        if serial_result['data']:
            return conflict_response("设备序列号已存在")
        
        # 插入新设备
        insert_sql = """
        INSERT INTO equipment (name, model, serial_number, laboratory_id, description, 
                             status, purchase_date, warranty_date, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        insert_result = execute_update(insert_sql, (
            name, model, serial_number, laboratory_id, description, 
            status, purchase_date, warranty_date
        ))
        
        if not insert_result['success']:
            logger.error(f"创建设备失败: {insert_result.get('error')}")
            return error_response("创建设备失败，请稍后重试")
        
        # 获取新创建的设备信息
        equipment_id = insert_result['last_insert_id']
        equipment_sql = """
        SELECT e.id, e.name, e.model, e.serial_number, e.description, e.status, 
               e.purchase_date, e.warranty_date, e.created_at,
               l.name as laboratory_name, l.location as laboratory_location
        FROM equipment e
        LEFT JOIN laboratories l ON e.laboratory_id = l.id
        WHERE e.id = %s
        """
        equipment_result = execute_query(equipment_sql, (equipment_id,))
        
        if equipment_result['success'] and equipment_result['data']:
            eq = equipment_result['data'][0]
            equipment_info = {
                'id': eq['id'],
                'name': eq['name'],
                'model': eq['model'],
                'serial_number': eq['serial_number'],
                'description': eq['description'],
                'status': eq['status'],
                'purchase_date': eq['purchase_date'].isoformat() if eq['purchase_date'] else None,
                'warranty_date': eq['warranty_date'].isoformat() if eq['warranty_date'] else None,
                'laboratory': {
                    'name': eq['laboratory_name'],
                    'location': eq['laboratory_location']
                } if eq['laboratory_name'] else None,
                'created_at': eq['created_at'].isoformat() if eq['created_at'] else None
            }
            
            return created_response(equipment_info, "设备创建成功")
        
        return created_response(None, "设备创建成功")
        
    except Exception as e:
        logger.error(f"创建设备接口错误: {str(e)}")
        return error_response("创建设备失败，请稍后重试")

@equipment_bp.route('/<int:equipment_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'name': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'model': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'serial_number': {'required': False, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'laboratory_id': {'required': False, 'type': 'integer', 'min_value': 1},
    'description': {'required': False, 'type': 'string', 'max_length': 500},
    'status': {'required': False, 'type': 'string', 'choices': ['available', 'maintenance', 'damaged', 'retired']},
    'purchase_date': {'required': False, 'type': 'date_string'},
    'warranty_date': {'required': False, 'type': 'date_string'}
})
def update_equipment(equipment_id):
    """更新设备信息"""
    try:
        data = request.validated_data
        
        # 检查设备是否存在
        check_sql = "SELECT id FROM equipment WHERE id = %s"
        check_result = execute_query(check_sql, (equipment_id,))
        
        if not check_result['success']:
            return error_response("更新失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("设备不存在")
        
        # 构建更新字段
        update_fields = []
        update_values = []
        
        if 'name' in data and data['name'] is not None:
            update_fields.append('name = %s')
            update_values.append(data['name'])
        
        if 'model' in data and data['model'] is not None:
            update_fields.append('model = %s')
            update_values.append(data['model'])
        
        if 'serial_number' in data and data['serial_number'] is not None:
            # 检查序列号是否已被其他设备使用
            serial_check_sql = "SELECT id FROM equipment WHERE serial_number = %s AND id != %s"
            serial_check_result = execute_query(serial_check_sql, (data['serial_number'], equipment_id))
            
            if not serial_check_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if serial_check_result['data']:
                return conflict_response("设备序列号已被使用")
            
            update_fields.append('serial_number = %s')
            update_values.append(data['serial_number'])
        
        if 'laboratory_id' in data and data['laboratory_id'] is not None:
            # 检查实验室是否存在
            lab_check_sql = "SELECT id FROM laboratories WHERE id = %s"
            lab_result = execute_query(lab_check_sql, (data['laboratory_id'],))
            
            if not lab_result['success']:
                return error_response("更新失败，请稍后重试")
            
            if not lab_result['data']:
                return error_response("指定的实验室不存在")
            
            update_fields.append('laboratory_id = %s')
            update_values.append(data['laboratory_id'])
        
        if 'description' in data and data['description'] is not None:
            update_fields.append('description = %s')
            update_values.append(data['description'])
        
        if 'status' in data and data['status'] is not None:
            update_fields.append('status = %s')
            update_values.append(data['status'])
        
        if 'purchase_date' in data and data['purchase_date'] is not None:
            update_fields.append('purchase_date = %s')
            update_values.append(data['purchase_date'])
        
        if 'warranty_date' in data and data['warranty_date'] is not None:
            update_fields.append('warranty_date = %s')
            update_values.append(data['warranty_date'])
        
        if not update_fields:
            return error_response("没有需要更新的字段")
        
        # 添加更新时间
        update_fields.append('updated_at = NOW()')
        update_values.append(equipment_id)
        
        # 执行更新
        update_sql = f"UPDATE equipment SET {', '.join(update_fields)} WHERE id = %s"
        update_result = execute_update(update_sql, tuple(update_values))
        
        if not update_result['success']:
            logger.error(f"更新设备信息失败: {update_result.get('error')}")
            return error_response("更新失败，请稍后重试")
        
        # 获取更新后的设备信息
        equipment_sql = """
        SELECT e.id, e.name, e.model, e.serial_number, e.description, e.status, 
               e.purchase_date, e.warranty_date, e.created_at, e.updated_at,
               l.name as laboratory_name, l.location as laboratory_location
        FROM equipment e
        LEFT JOIN laboratories l ON e.laboratory_id = l.id
        WHERE e.id = %s
        """
        equipment_result = execute_query(equipment_sql, (equipment_id,))
        
        if equipment_result['success'] and equipment_result['data']:
            eq = equipment_result['data'][0]
            equipment_info = {
                'id': eq['id'],
                'name': eq['name'],
                'model': eq['model'],
                'serial_number': eq['serial_number'],
                'description': eq['description'],
                'status': eq['status'],
                'purchase_date': eq['purchase_date'].isoformat() if eq['purchase_date'] else None,
                'warranty_date': eq['warranty_date'].isoformat() if eq['warranty_date'] else None,
                'laboratory': {
                    'name': eq['laboratory_name'],
                    'location': eq['laboratory_location']
                } if eq['laboratory_name'] else None,
                'created_at': eq['created_at'].isoformat() if eq['created_at'] else None,
                'updated_at': eq['updated_at'].isoformat() if eq['updated_at'] else None
            }
            
            return updated_response(equipment_info, "设备信息更新成功")
        
        return updated_response(None, "设备信息更新成功")
        
    except Exception as e:
        logger.error(f"更新设备信息接口错误: {str(e)}")
        return error_response("更新失败，请稍后重试")

@equipment_bp.route('/<int:equipment_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_equipment(equipment_id):
    """删除设备"""
    try:
        # 检查设备是否存在
        check_sql = "SELECT id, name FROM equipment WHERE id = %s"
        check_result = execute_query(check_sql, (equipment_id,))
        
        if not check_result['success']:
            return error_response("删除失败，请稍后重试")
        
        if not check_result['data']:
            return not_found_response("设备不存在")
        
        # 检查设备是否有相关的预约记录
        reservation_check_sql = """
        SELECT COUNT(*) as count 
        FROM reservations 
        WHERE equipment_ids LIKE %s OR equipment_ids LIKE %s OR equipment_ids LIKE %s OR equipment_ids = %s
        """
        equipment_id_str = str(equipment_id)
        reservation_result = execute_query(reservation_check_sql, (
            f'%,{equipment_id_str},%',  # 中间
            f'{equipment_id_str},%',    # 开头
            f'%,{equipment_id_str}',    # 结尾
            equipment_id_str            # 单独
        ))
        
        if reservation_result['success'] and reservation_result['data']:
            reservation_count = reservation_result['data'][0]['count']
            if reservation_count > 0:
                return error_response("该设备有相关的预约记录，无法删除")
        
        # 删除设备
        delete_sql = "DELETE FROM equipment WHERE id = %s"
        delete_result = execute_update(delete_sql, (equipment_id,))
        
        if not delete_result['success']:
            logger.error(f"删除设备失败: {delete_result.get('error')}")
            return error_response("删除失败，请稍后重试")
        
        return deleted_response("设备删除成功")
        
    except Exception as e:
        logger.error(f"删除设备接口错误: {str(e)}")
        return error_response("删除失败，请稍后重试")

@equipment_bp.route('/statistics', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
def get_equipment_statistics():
    """获取设备统计信息"""
    try:
        # 按状态统计设备数量
        status_sql = """
        SELECT status, COUNT(*) as count
        FROM equipment
        GROUP BY status
        """
        status_result = execute_query(status_sql, ())
        
        if not status_result['success']:
            logger.error(f"查询设备状态统计失败: {status_result.get('error')}")
            return error_response("获取统计信息失败")
        
        status_stats = {}
        total_count = 0
        for row in status_result['data']:
            status_stats[row['status']] = row['count']
            total_count += row['count']
        
        # 按实验室统计设备数量
        lab_sql = """
        SELECT l.name as laboratory_name, COUNT(e.id) as count
        FROM laboratories l
        LEFT JOIN equipment e ON l.id = e.laboratory_id
        GROUP BY l.id, l.name
        ORDER BY count DESC
        """
        lab_result = execute_query(lab_sql, ())
        
        lab_stats = []
        if lab_result['success']:
            for row in lab_result['data']:
                lab_stats.append({
                    'laboratory_name': row['laboratory_name'],
                    'equipment_count': row['count']
                })
        
        # 即将过保的设备（30天内）
        warranty_sql = """
        SELECT id, name, model, warranty_date, DATEDIFF(warranty_date, CURDATE()) as days_left
        FROM equipment
        WHERE warranty_date IS NOT NULL 
        AND warranty_date > CURDATE() 
        AND DATEDIFF(warranty_date, CURDATE()) <= 30
        ORDER BY warranty_date ASC
        """
        warranty_result = execute_query(warranty_sql, ())
        
        warranty_expiring = []
        if warranty_result['success']:
            for row in warranty_result['data']:
                warranty_expiring.append({
                    'id': row['id'],
                    'name': row['name'],
                    'model': row['model'],
                    'warranty_date': row['warranty_date'].isoformat() if row['warranty_date'] else None,
                    'days_left': row['days_left']
                })
        
        statistics = {
            'total_equipment': total_count,
            'status_distribution': status_stats,
            'laboratory_distribution': lab_stats,
            'warranty_expiring_soon': warranty_expiring
        }
        
        return success_response(statistics, "获取设备统计信息成功")
        
    except Exception as e:
        logger.error(f"获取设备统计信息接口错误: {str(e)}")
        return error_response("获取统计信息失败")