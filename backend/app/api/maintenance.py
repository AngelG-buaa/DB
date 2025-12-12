#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备维修记录 API 接口（基于 equipment_repair 表）
提供列表查询、详情、创建、更新、删除与统计接口
"""

from flask import Blueprint, request
from datetime import datetime, date
from backend.database import execute_query, execute_update, execute_paginated_query, execute_transaction
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

# 创建蓝图（在 app.py 中以 /api/equipment/maintenance 注册）
maintenance_bp = Blueprint('maintenance', __name__)


def _map_record(row):
    """将数据库行映射为前端期望的字段名与格式"""
    # 将 repair_status 中的 reported 视作 in_progress
    status = row.get('repair_status')
    if status == 'reported':
        status = 'in_progress'

    def _to_date_string(value):
        if not value:
            return None
        if isinstance(value, (datetime, date)):
            return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
        try:
            return str(value)[:10]
        except Exception:
            return None

    return {
        'id': row.get('id'),
        'equipment_id': row.get('equipment_id'),
        'type': row.get('repair_type') or 'repair',
        'description': row.get('fault_description') or '',
        'technician': row.get('repair_person') or '',
        'cost': float(row.get('repair_cost') or 0),
        'start_date': _to_date_string(row.get('start_time')),
        'expected_completion_date': _to_date_string(row.get('expected_finish_date')),
        'actual_completion_date': _to_date_string(row.get('finish_time')),
        'status': status,
        'remarks': row.get('remarks') or row.get('repair_description') or '',
        'created_at': row.get('created_at').isoformat() if row.get('created_at') else None,
        'updated_at': row.get('updated_at').isoformat() if row.get('updated_at') else None,
        # 附加设备信息（若联结查询返回）
        'equipment_name': row.get('equipment_name'),
        'equipment_model': row.get('equipment_model')
    }


@maintenance_bp.route('', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 20},
    'keyword': {'type': 'string', 'max_length': 100},
    'equipment_id': {'type': 'integer', 'min_value': 1},
    'type': {'type': 'string', 'choices': ['maintenance', 'repair', 'upgrade']},
    'status': {'type': 'string', 'choices': ['in_progress', 'completed', 'cancelled']},
    'start_date': {'type': 'date_string'},
    'end_date': {'type': 'date_string'}
})
def list_maintenance_records():
    """分页获取维修记录列表"""
    try:
        params = request.validated_params
        page = params['page']
        page_size = params['size']
        keyword = params.get('keyword')
        equipment_id = params.get('equipment_id')
        m_type = params.get('type')
        status = params.get('status')
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        where = []
        qparams = []

        if keyword:
            where.append('(e.name LIKE %s OR r.repair_person LIKE %s)')
            kw = f"%{keyword}%"
            qparams.extend([kw, kw])

        if equipment_id:
            where.append('r.equipment_id = %s')
            qparams.append(equipment_id)

        if m_type:
            where.append('COALESCE(r.repair_type, "repair") = %s')
            qparams.append(m_type)

        if status:
            # reported 也视作 in_progress
            if status == 'in_progress':
                where.append('(r.repair_status = "in_progress" OR r.repair_status = "reported")')
            else:
                where.append('r.repair_status = %s')
                qparams.append(status)

        if start_date:
            where.append('DATE(r.start_time) >= %s')
            qparams.append(start_date)
        if end_date:
            where.append('DATE(r.start_time) <= %s')
            qparams.append(end_date)

        base_sql = (
            "SELECT r.id, r.equipment_id, r.repair_person, r.fault_description, r.repair_description, "
            "r.repair_cost, r.repair_status, r.priority, r.report_time, r.start_time, r.finish_time, "
            "r.expected_finish_date, r.remarks, r.created_at, r.updated_at, "
            "r.repair_type, e.name AS equipment_name, e.model AS equipment_model "
            "FROM equipment_repair r "
            "LEFT JOIN equipment e ON r.equipment_id = e.id "
        )

        if where:
            base_sql += ' WHERE ' + ' AND '.join(where)

        base_sql += ' ORDER BY r.start_time DESC, r.id DESC'

        result = execute_paginated_query(base_sql, tuple(qparams), page, page_size)
        if not result['success']:
            logger.error(f"查询维修记录失败: {result.get('error')}")
            return error_response('获取维修记录失败')

        records = [_map_record(row) for row in result['data']]
        return paginated_response(records, result['pagination'], '获取维修记录成功')
    except Exception as e:
        logger.error(f"获取维修记录接口错误: {str(e)}")
        return error_response('获取维修记录失败')


@maintenance_bp.route('/<int:record_id>', methods=['GET'])
@require_auth
def get_maintenance_detail(record_id):
    try:
        sql = (
            "SELECT r.*, e.name AS equipment_name, e.model AS equipment_model "
            "FROM equipment_repair r "
            "LEFT JOIN equipment e ON r.equipment_id = e.id "
            "WHERE r.id = %s"
        )
        result = execute_query(sql, (record_id,))
        if not result['success']:
            return error_response('获取维修记录失败')
        if not result['data']:
            return not_found_response('维修记录不存在')
        record = _map_record(result['data'][0])
        return success_response(record, '获取维修记录成功')
    except Exception as e:
        logger.error(f"获取维修记录详情错误: {str(e)}")
        return error_response('获取维修记录失败')


@maintenance_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'equipment_id': {'required': True, 'type': 'integer', 'min_value': 1},
    'type': {'required': False, 'type': 'string', 'choices': ['maintenance', 'repair', 'upgrade'], 'default': 'repair'},
    'description': {'required': True, 'type': 'string', 'min_length': 5, 'max_length': 1000},
    'technician': {'required': True, 'type': 'string', 'min_length': 2, 'max_length': 100},
    'cost': {'required': False, 'type': 'number'},
    'start_date': {'required': True, 'type': 'date'},
    'expected_completion_date': {'required': False, 'type': 'date'},
    'actual_completion_date': {'required': False, 'type': 'date'},
    'status': {'required': False, 'type': 'string', 'choices': ['in_progress', 'completed', 'cancelled'], 'default': 'in_progress'},
    'remarks': {'required': False, 'type': 'string', 'max_length': 1000},
    'repair_description': {'required': False, 'type': 'string', 'max_length': 1000}
})
def create_maintenance_record():
    try:
        data = request.validated_data
        current_user = request.current_user

        # 验证设备存在
        eq_res = execute_query("SELECT id FROM equipment WHERE id = %s", (data['equipment_id'],))
        if not eq_res['success']:
            return error_response('创建失败，请稍后重试')
        if not eq_res['data']:
            return error_response('指定设备不存在')

        insert_sql = (
            "INSERT INTO equipment_repair (equipment_id, reporter_id, repair_person, fault_description, "
            "repair_description, repair_cost, repair_status, priority, report_time, start_time, finish_time, "
            "expected_finish_date, remarks, repair_type, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, 'medium', NOW(), %s, %s, %s, %s, %s, NOW())"
        )

        # 状态映射
        status = data.get('status', 'in_progress')
        if status not in ['in_progress', 'completed', 'cancelled']:
            status = 'in_progress'

        insert_params = (
            data['equipment_id'],
            (current_user.get('id') or current_user.get('user_id')),
            data['technician'],
            data['description'],
            (data.get('repair_description') or ''),
            data.get('cost'),
            status,
            (data.get('start_date') or None),
            data.get('actual_completion_date'),
            data.get('expected_completion_date'),
            data.get('remarks'),
            data.get('type', 'repair')
        )

        # 使用事务：创建维修记录 + 更新设备状态
        transaction_ops = [
            (insert_sql, insert_params)
        ]

        # 如果维修状态是进行中，则将设备状态更新为维护中
        if status in ['in_progress', 'reported']:
            transaction_ops.append((
                "UPDATE equipment SET status = 'maintenance', updated_at = NOW() WHERE id = %s",
                (data['equipment_id'],)
            ))
        
        result = execute_transaction(transaction_ops)
        
        if not result['success']:
            logger.error(f"插入维修记录失败: {result.get('error')}")
            return error_response('创建维修记录失败')

        # 获取新插入的记录ID (第一个操作的结果)
        new_id = result['results'][0]['last_insert_id']
        
        detail = execute_query(
            "SELECT r.*, e.name AS equipment_name, e.model AS equipment_model "
            "FROM equipment_repair r LEFT JOIN equipment e ON r.equipment_id = e.id WHERE r.id = %s",
            (new_id,)
        )
        record = _map_record(detail['data'][0]) if (detail['success'] and detail['data']) else None
        return created_response(record, '创建维修记录成功')
    except Exception as e:
        logger.error(f"创建维修记录接口错误: {str(e)}")
        return error_response('创建维修记录失败')


@maintenance_bp.route('/<int:record_id>', methods=['PUT'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'equipment_id': {'required': False, 'type': 'integer', 'min_value': 1},
    'type': {'required': False, 'type': 'string', 'choices': ['maintenance', 'repair', 'upgrade']},
    'description': {'required': False, 'type': 'string', 'min_length': 5, 'max_length': 1000},
    'technician': {'required': False, 'type': 'string', 'min_length': 2, 'max_length': 100},
    'cost': {'required': False, 'type': 'number'},
    'start_date': {'required': False, 'type': 'date'},
    'expected_completion_date': {'required': False, 'type': 'date'},
    'actual_completion_date': {'required': False, 'type': 'date'},
    'status': {'required': False, 'type': 'string', 'choices': ['in_progress', 'completed', 'cancelled']},
    'remarks': {'required': False, 'type': 'string', 'max_length': 1000},
    'repair_description': {'required': False, 'type': 'string', 'max_length': 1000}
})
def update_maintenance_record(record_id):
    try:
        data = request.validated_data

        # 检查记录存在
        check = execute_query("SELECT id, equipment_id FROM equipment_repair WHERE id = %s", (record_id,))
        if not check['success']:
            return error_response('更新失败，请稍后重试')
        if not check['data']:
            return not_found_response('维修记录不存在')

        equipment_id = check['data'][0]['equipment_id']
        fields = []
        params = []

        mapping = {
            'equipment_id': ('equipment_id', None),
            'type': ('repair_type', None),
            'description': ('fault_description', None),
            'technician': ('repair_person', None),
            'cost': ('repair_cost', None),
            'start_date': ('start_time', None),
            'expected_completion_date': ('expected_finish_date', None),
            'actual_completion_date': ('finish_time', None),
            'remarks': ('remarks', None),
            'repair_description': ('repair_description', None),
        }

        for key, (col, _) in mapping.items():
            if key in data:
                val = data.get(key)
                # 跳过空字符串或 None，避免将已有值覆盖为 NULL
                if val is None:
                    continue
                if isinstance(val, str) and val.strip() == '':
                    continue
                fields.append(f"{col} = %s")
                params.append(val)

        if 'status' in data:
            fields.append("repair_status = %s")
            params.append(data['status'])

        if not fields:
            return success_response(None, '无需更新')

        sql = f"UPDATE equipment_repair SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s"
        params.append(record_id)
        
        # 使用事务
        transaction_ops = [
            (sql, tuple(params))
        ]
        
        # 如果更新了状态，同步更新设备状态
        if 'status' in data:
            new_status = data['status']
            if new_status in ['in_progress', 'reported']:
                transaction_ops.append((
                    "UPDATE equipment SET status = 'maintenance', updated_at = NOW() WHERE id = %s",
                    (equipment_id,)
                ))
            elif new_status in ['completed', 'cancelled']:
                transaction_ops.append((
                    "UPDATE equipment SET status = 'available', updated_at = NOW() WHERE id = %s",
                    (equipment_id,)
                ))
        
        result = execute_transaction(transaction_ops)
        if not result['success']:
            logger.error(f"更新维修记录失败: {result.get('error')}")
            return error_response('更新维修记录失败')

        # 返回最新详情
        detail = execute_query(
            "SELECT r.*, e.name AS equipment_name, e.model AS equipment_model "
            "FROM equipment_repair r LEFT JOIN equipment e ON r.equipment_id = e.id WHERE r.id = %s",
            (record_id,)
        )
        record = _map_record(detail['data'][0]) if (detail['success'] and detail['data']) else None
        return updated_response(record, '更新维修记录成功')
    except Exception as e:
        logger.error(f"更新维修记录接口错误: {str(e)}")
        return error_response('更新维修记录失败')


@maintenance_bp.route('/<int:record_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_maintenance_record(record_id):
    try:
        result = execute_update("DELETE FROM equipment_repair WHERE id = %s", (record_id,))
        if not result['success']:
            return error_response('删除维修记录失败')
        if result.get('affected_rows', 0) == 0:
            return not_found_response('维修记录不存在')
        return deleted_response(None, '删除维修记录成功')
    except Exception as e:
        logger.error(f"删除维修记录接口错误: {str(e)}")
        return error_response('删除维修记录失败')


@maintenance_bp.route('/stats', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
def maintenance_statistics():
    try:
        # 总数
        total_res = execute_query("SELECT COUNT(*) AS cnt FROM equipment_repair")
        # 进行中（含 reported）
        in_progress_res = execute_query(
            "SELECT COUNT(*) AS cnt FROM equipment_repair WHERE repair_status IN ('reported', 'in_progress')"
        )
        # 本月启动数量
        month_res = execute_query(
            "SELECT COUNT(*) AS cnt FROM equipment_repair WHERE YEAR(start_time) = YEAR(CURDATE()) AND MONTH(start_time) = MONTH(CURDATE())"
        )
        # 总费用
        cost_res = execute_query("SELECT COALESCE(SUM(repair_cost), 0) AS total_cost FROM equipment_repair")

        stats = {
            'total': (total_res['data'][0]['cnt'] if total_res['success'] and total_res['data'] else 0),
            'inProgress': (in_progress_res['data'][0]['cnt'] if in_progress_res['success'] and in_progress_res['data'] else 0),
            'thisMonth': (month_res['data'][0]['cnt'] if month_res['success'] and month_res['data'] else 0),
            'totalCost': float(cost_res['data'][0]['total_cost'] if cost_res['success'] and cost_res['data'] else 0)
        }
        return success_response(stats, '获取维修统计成功')
    except Exception as e:
        logger.error(f"维修统计接口错误: {str(e)}")
        return error_response('获取维修统计失败')


@maintenance_bp.route('/<int:record_id>/complete', methods=['POST'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_json_data({
    'actual_completion_date': {'required': False, 'type': 'date_string'},
    'remarks': {'required': False, 'type': 'string', 'max_length': 1000},
    'cost': {'required': False, 'type': 'number'}
})
def complete_maintenance_record(record_id):
    """将维修记录标记为完成，并可更新完成时间、备注与费用"""
    try:
        data = request.validated_data

        # 检查记录存在
        check = execute_query("SELECT id, equipment_id FROM equipment_repair WHERE id = %s", (record_id,))
        if not check['success']:
            return error_response('完成失败，请稍后重试')
        if not check['data']:
            return not_found_response('维修记录不存在')

        fields = ["repair_status = 'completed'"]
        params = []

        if 'actual_completion_date' in data:
            fields.append("finish_time = %s")
            params.append(data['actual_completion_date'])
        else:
            # 若未提供，设置为当前时间
            fields.append("finish_time = NOW()")

        if 'remarks' in data:
            fields.append("remarks = %s")
            params.append(data['remarks'])

        if 'cost' in data:
            fields.append("repair_cost = %s")
            params.append(data['cost'])

        sql = f"UPDATE equipment_repair SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s"
        params.append(record_id)
        
        # 使用事务：更新维修记录 + 更新设备状态为可用
        equipment_id = check['data'][0]['equipment_id']
        transaction_ops = [
            (sql, tuple(params)),
            ("UPDATE equipment SET status = 'available', updated_at = NOW() WHERE id = %s", (equipment_id,))
        ]
        
        result = execute_transaction(transaction_ops)
        if not result['success']:
            return error_response('更新维修完成状态失败')

        # 返回最新详情
        detail = execute_query(
            "SELECT r.*, e.name AS equipment_name, e.model AS equipment_model "
            "FROM equipment_repair r LEFT JOIN equipment e ON r.equipment_id = e.id WHERE r.id = %s",
            (record_id,)
        )
        record = _map_record(detail['data'][0]) if (detail['success'] and detail['data']) else None
        return updated_response(record, '维修记录已完成')
    except Exception as e:
        logger.error(f"完成维修记录接口错误: {str(e)}")
        return error_response('完成维修记录失败')

@maintenance_bp.route('/trend', methods=['GET'])
@require_auth
@require_role(['admin', 'teacher'])
@validate_query_params({
    'months': {'type': 'integer', 'min_value': 1, 'max_value': 24, 'default': 6}
})
def maintenance_trend():
    try:
        params = request.validated_params
        months = params.get('months', 6)

        trend_sql = (
            "SELECT DATE_FORMAT(COALESCE(finish_time, start_time, report_time, created_at), '%Y-%m') AS ym, "
            "       COUNT(*) AS count, COALESCE(SUM(repair_cost), 0) AS total_cost "
            "FROM equipment_repair "
            f"WHERE COALESCE(finish_time, start_time, report_time, created_at) >= DATE_SUB(CURDATE(), INTERVAL {months} MONTH) "
            "GROUP BY ym ORDER BY ym ASC"
        )
        result = execute_query(trend_sql, ())
        data_map = {}
        if not result['success']:
            logger.error(f"维修趋势查询失败: {result.get('error')}")
        else:
            data_map = {row['ym']: {'month': row['ym'], 'count': row['count'], 'total_cost': float(row['total_cost'])} for row in (result['data'] or [])}

        from datetime import datetime
        months_list = []
        now = datetime.now()
        y = now.year
        m = now.month
        seq = []
        for i in range(months-1, -1, -1):
            mm = m - i
            yy = y
            while mm <= 0:
                yy -= 1
                mm += 12
            seq.append((yy, mm))
        for yy, mm in seq:
            months_list.append(f"{yy}-{mm:02d}")

        series = []
        for ym in months_list:
            v = data_map.get(ym, {'month': ym, 'count': 0, 'total_cost': 0.0})
            series.append(v)

        return success_response({'months': months_list, 'series': series}, '获取维修趋势成功')
    except Exception as e:
        logger.error(f"维修趋势接口错误: {str(e)}")
        return error_response('获取维修趋势失败')
