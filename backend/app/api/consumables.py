#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request
from backend.init_database import execute_query, execute_update, execute_paginated_query
from app.utils import (
    require_auth, require_role, validate_json_data, validate_query_params,
    success_response, error_response, not_found_response,
    paginated_response, created_response, updated_response, deleted_response
)
import logging

logger = logging.getLogger(__name__)

consumables_bp = Blueprint('consumables', __name__)

@consumables_bp.route('', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'search': {'type': 'string', 'max_length': 100},
    'keyword': {'type': 'string', 'max_length': 100},
    'laboratory_id': {'type': 'integer', 'min_value': 1},
    'labId': {'type': 'integer', 'min_value': 1},
    'status': {'type': 'string', 'choices': ['normal','low_stock','out_of_stock']},
    'date_from': {'type': 'string'},
    'date_to': {'type': 'string'},
    'startDate': {'type': 'string'},
    'endDate': {'type': 'string'}
})
def list_consumables():
    try:
        p = request.validated_params
        page = p['page']
        page_size = p['page_size']
        where = []
        params = []

        search = p.get('search') or p.get('keyword')
        lab_id = p.get('laboratory_id') or p.get('labId')
        date_from = p.get('date_from') or p.get('startDate')
        date_to = p.get('date_to') or p.get('endDate')

        if search:
            where.append('(c.name LIKE %s OR c.model LIKE %s OR c.supplier LIKE %s)')
            kw = f"%{search}%"
            params.extend([kw, kw, kw])
        if lab_id:
            where.append('c.laboratory_id = %s')
            params.append(lab_id)
        if p.get('status'):
            where.append('c.status = %s')
            params.append(p['status'])
        if date_from:
            where.append('c.purchase_date >= %s')
            params.append(date_from)
        if date_to:
            where.append('c.purchase_date <= %s')
            params.append(date_to)

        base_sql = (
            "SELECT c.id, c.name, c.model, c.laboratory_id, l.name AS lab_name, "
            "c.unit, c.unit_price, c.current_stock, c.min_stock, c.supplier, "
            "c.purchase_date, c.description, c.status, c.usage_count, c.created_at, c.updated_at "
            "FROM consumables c LEFT JOIN laboratories l ON c.laboratory_id = l.id "
        )
        if where:
            base_sql += ' WHERE ' + ' AND '.join(where)
        base_sql += ' ORDER BY c.created_at DESC, c.id DESC'

        result = execute_paginated_query(base_sql, tuple(params), page, page_size)
        if not result['success']:
            logger.error(f"查询耗材列表失败: {result.get('error')}")
            return error_response('获取耗材列表失败')

        items = []
        for r in result['data']:
            items.append({
                'id': r.get('id'),
                'name': r.get('name'),
                'model': r.get('model'),
                'labId': r.get('laboratory_id'),
                'labName': r.get('lab_name'),
                'unit': r.get('unit'),
                'unitPrice': float(r.get('unit_price') or 0),
                'currentStock': float(r.get('current_stock') or 0),
                'minStock': float(r.get('min_stock') or 0),
                'supplier': r.get('supplier'),
                'purchaseDate': r.get('purchase_date').isoformat() if r.get('purchase_date') else None,
                'description': r.get('description'),
                'status': r.get('status'),
                'usageCount': int(r.get('usage_count') or 0),
                'createdAt': r.get('created_at').isoformat() if r.get('created_at') else None,
                'updatedAt': r.get('updated_at').isoformat() if r.get('updated_at') else None,
            })
        return paginated_response(items, result['pagination'], '获取耗材列表成功')
    except Exception as e:
        logger.error(f"获取耗材列表接口错误: {str(e)}")
        return error_response('获取耗材列表失败')

@consumables_bp.route('/<int:cid>', methods=['GET'])
@require_auth
def get_consumable(cid):
    try:
        sql = (
            "SELECT c.id, c.name, c.model, c.laboratory_id, l.name AS lab_name, c.unit, c.unit_price, "
            "c.current_stock, c.min_stock, c.supplier, c.purchase_date, c.description, c.status, c.usage_count, c.created_at, c.updated_at "
            "FROM consumables c LEFT JOIN laboratories l ON c.laboratory_id = l.id WHERE c.id = %s"
        )
        res = execute_query(sql, (cid,))
        if not res['success']:
            return error_response('获取耗材详情失败')
        if not res['data']:
            return not_found_response('耗材不存在')
        r = res['data'][0]
        d = {
            'id': r.get('id'),
            'name': r.get('name'),
            'model': r.get('model'),
            'labId': r.get('laboratory_id'),
            'labName': r.get('lab_name'),
            'unit': r.get('unit'),
            'unitPrice': float(r.get('unit_price') or 0),
            'currentStock': float(r.get('current_stock') or 0),
            'minStock': float(r.get('min_stock') or 0),
            'supplier': r.get('supplier'),
            'purchaseDate': r.get('purchase_date').isoformat() if r.get('purchase_date') else None,
            'description': r.get('description'),
            'status': r.get('status'),
            'usageCount': int(r.get('usage_count') or 0),
            'createdAt': r.get('created_at').isoformat() if r.get('created_at') else None,
            'updatedAt': r.get('updated_at').isoformat() if r.get('updated_at') else None,
        }
        return success_response(d, '获取耗材详情成功')
    except Exception as e:
        logger.error(f"获取耗材详情接口错误: {str(e)}")
        return error_response('获取耗材详情失败')

@consumables_bp.route('', methods=['POST'])
@require_auth
@require_role(['admin','teacher'])
@validate_json_data({
    'name': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'model': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 100},
    'laboratory_id': {'required': True, 'type': 'integer', 'min_value': 1},
    'unit': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 20},
    'unit_price': {'required': True, 'type': 'float', 'min_value': 0},
    'current_stock': {'required': True, 'type': 'float', 'min_value': 0},
    'min_stock': {'required': True, 'type': 'float', 'min_value': 0},
    'supplier': {'required': False, 'type': 'string', 'max_length': 100},
    'purchase_date': {'required': True, 'type': 'date_string'},
    'description': {'required': False, 'type': 'string', 'max_length': 500}
})
def create_consumable():
    try:
        d = request.validated_data
        status = 'normal'
        cs = float(d['current_stock'] or 0)
        ms = float(d['min_stock'] or 0)
        if cs <= 0:
            status = 'out_of_stock'
        elif cs <= ms:
            status = 'low_stock'

        insert = (
            "INSERT INTO consumables (name, model, laboratory_id, unit, unit_price, current_stock, min_stock, supplier, purchase_date, description, status, usage_count, created_at) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,NOW())"
        )
        params = (d['name'], d['model'], d['laboratory_id'], d['unit'], d['unit_price'], d['current_stock'], d['min_stock'], d.get('supplier'), d['purchase_date'], d.get('description'), status)
        r = execute_update(insert, params)
        if not r['success']:
            logger.error(f"创建耗材失败: {r.get('error')}")
            return error_response('创建耗材失败')
        new_id = r.get('last_insert_id')
        if new_id:
            q = (
                "SELECT c.id, c.name, c.model, c.laboratory_id, l.name AS lab_name, "
                "c.unit, c.unit_price, c.current_stock, c.min_stock, c.supplier, "
                "c.purchase_date, c.description, c.status, c.usage_count, c.created_at "
                "FROM consumables c LEFT JOIN laboratories l ON c.laboratory_id = l.id WHERE c.id = %s"
            )
            res = execute_query(q, (new_id,))
            if res['success'] and res['data']:
                r0 = res['data'][0]
                d0 = {
                    'id': r0.get('id'),
                    'name': r0.get('name'),
                    'model': r0.get('model'),
                    'labId': r0.get('laboratory_id'),
                    'labName': r0.get('lab_name'),
                    'unit': r0.get('unit'),
                    'unitPrice': float(r0.get('unit_price') or 0),
                    'currentStock': float(r0.get('current_stock') or 0),
                    'minStock': float(r0.get('min_stock') or 0),
                    'supplier': r0.get('supplier'),
                    'purchaseDate': r0.get('purchase_date').isoformat() if r0.get('purchase_date') else None,
                    'description': r0.get('description'),
                    'status': r0.get('status'),
                    'usageCount': int(r0.get('usage_count') or 0),
                    'createdAt': r0.get('created_at').isoformat() if r0.get('created_at') else None,
                }
                return created_response(d0, '耗材创建成功')
        return created_response(None, '耗材创建成功')
    except Exception as e:
        logger.error(f"创建耗材接口错误: {str(e)}")
        return error_response('创建耗材失败')

@consumables_bp.route('/<int:cid>', methods=['PUT'])
@require_auth
@require_role(['admin','teacher'])
def update_consumable(cid):
    try:
        data = request.get_json() or {}
        fields = []
        params = []
        mapping = {
            'name':'name','model':'model','laboratory_id':'laboratory_id','unit':'unit','unit_price':'unit_price',
            'current_stock':'current_stock','min_stock':'min_stock','supplier':'supplier','purchase_date':'purchase_date','description':'description','status':'status'
        }
        for k, col in mapping.items():
            if k in data and data[k] is not None:
                fields.append(f"{col} = %s")
                params.append(data[k])
        if not fields:
            return error_response('没有需要更新的字段')
        fields.append('updated_at = NOW()')
        params.append(cid)
        sql = f"UPDATE consumables SET {', '.join(fields)} WHERE id = %s"
        r = execute_update(sql, tuple(params))
        if not r['success']:
            logger.error(f"更新耗材失败: {r.get('error')}")
            return error_response('更新耗材失败')
        return updated_response(None, '更新成功')
    except Exception as e:
        logger.error(f"更新耗材接口错误: {str(e)}")
        return error_response('更新耗材失败')

@consumables_bp.route('/<int:cid>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def delete_consumable(cid):
    try:
        r = execute_update("DELETE FROM consumables WHERE id = %s", (cid,))
        if not r['success']:
            return error_response('删除耗材失败')
        if r.get('affected_rows', 0) == 0:
            return not_found_response('耗材不存在')
        return deleted_response('删除成功')
    except Exception as e:
        logger.error(f"删除耗材接口错误: {str(e)}")
        return error_response('删除耗材失败')

@consumables_bp.route('/<int:cid>/use', methods=['POST'])
@require_auth
@require_role(['admin','teacher'])
@validate_json_data({
    'quantity': {'required': True, 'type': 'float', 'min_value': 0},
    'userId': {'required': True, 'type': 'integer', 'min_value': 1},
    'purpose': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 200}
})
def use_consumable(cid):
    try:
        d = request.validated_data
        # 获取当前库存
        cur = execute_query("SELECT current_stock FROM consumables WHERE id = %s", (cid,))
        if not cur['success'] or not cur['data']:
            return not_found_response('耗材不存在')
        stock = float(cur['data'][0]['current_stock'] or 0)
        qty = float(d['quantity'])
        if qty <= 0 or stock < qty:
            return error_response('库存不足或数量非法')
        # 扣减库存并增加使用次数
        u1 = execute_update("UPDATE consumables SET current_stock = current_stock - %s, usage_count = usage_count + 1, updated_at = NOW() WHERE id = %s", (qty, cid))
        if not u1['success']:
            return error_response('更新库存失败')
        # 写入使用记录
        u2 = execute_update(
            "INSERT INTO consumable_usage (consumable_id, user_id, quantity, purpose, created_at) VALUES (%s,%s,%s,%s,NOW())",
            (cid, d['userId'], qty, d['purpose'])
        )
        if not u2['success']:
            logger.error(f"保存使用记录失败: {u2.get('error')}")
        return updated_response(None, '使用记录已保存')
    except Exception as e:
        logger.error(f"使用耗材接口错误: {str(e)}")
        return error_response('保存使用记录失败')

@consumables_bp.route('/<int:cid>/restock', methods=['POST'])
@require_auth
@require_role(['admin','teacher'])
@validate_json_data({
    'quantity': {'required': True, 'type': 'float', 'min_value': 0},
    'unitPrice': {'required': False, 'type': 'float', 'min_value': 0},
    'supplier': {'required': False, 'type': 'string', 'max_length': 100},
    'remarks': {'required': False, 'type': 'string', 'max_length': 500}
})
def restock_consumable(cid):
    try:
        d = request.validated_data
        fields = ["current_stock = current_stock + %s"]
        params = [float(d['quantity'])]
        if d.get('unitPrice') is not None:
            fields.append("unit_price = %s")
            params.append(d['unitPrice'])
        if d.get('supplier'):
            fields.append("supplier = %s")
            params.append(d['supplier'])
        fields.append('updated_at = NOW()')
        params.append(cid)
        sql = f"UPDATE consumables SET {', '.join(fields)} WHERE id = %s"
        r = execute_update(sql, tuple(params))
        if not r['success']:
            return error_response('补货失败')
        return updated_response(None, '补货成功')
    except Exception as e:
        logger.error(f"补货接口错误: {str(e)}")
        return error_response('补货失败')

@consumables_bp.route('/stats', methods=['GET'])
@require_auth
def consumable_stats():
    try:
        total = execute_query("SELECT COUNT(*) AS cnt FROM consumables")
        low = execute_query("SELECT COUNT(*) AS cnt FROM consumables WHERE current_stock <= min_stock")
        monthly = execute_query("SELECT COUNT(*) AS cnt FROM consumable_usage WHERE DATE_FORMAT(created_at,'%Y-%m') = DATE_FORMAT(CURDATE(),'%Y-%m')")
        value = execute_query("SELECT COALESCE(SUM(current_stock*unit_price),0) AS val FROM consumables")
        data = {
            'total': (total['data'][0]['cnt'] if total['success'] and total['data'] else 0),
            'lowStock': (low['data'][0]['cnt'] if low['success'] and low['data'] else 0),
            'monthlyUsage': (monthly['data'][0]['cnt'] if monthly['success'] and monthly['data'] else 0),
            'totalValue': float(value['data'][0]['val'] if value['success'] and value['data'] else 0),
        }
        return success_response(data, '获取耗材统计成功')
    except Exception as e:
        logger.error(f"耗材统计接口错误: {str(e)}")
        return error_response('获取耗材统计失败')

@consumables_bp.route('/usage', methods=['GET'])
@require_auth
@validate_query_params({
    'page': {'type': 'integer', 'min_value': 1, 'default': 1},
    'page_size': {'type': 'integer', 'min_value': 1, 'max_value': 1000, 'default': 10},
    'consumable_id': {'type': 'integer', 'min_value': 1},
    'consumableId': {'type': 'integer', 'min_value': 1},
    'user_id': {'type': 'integer', 'min_value': 1},
    'userId': {'type': 'integer', 'min_value': 1},
    'date_from': {'type': 'string'},
    'date_to': {'type': 'string'},
    'dateFrom': {'type': 'string'},
    'dateTo': {'type': 'string'},
    'search': {'type': 'string', 'max_length': 100},
    'keyword': {'type': 'string', 'max_length': 100}
})
def list_consumable_usage():
    try:
        p = request.validated_params
        page = p['page']
        page_size = p['page_size']
        where = []
        params = []

        cid = p.get('consumable_id') or p.get('consumableId')
        uid = p.get('user_id') or p.get('userId')
        date_from = p.get('date_from') or p.get('dateFrom')
        date_to = p.get('date_to') or p.get('dateTo')
        search = p.get('search') or p.get('keyword')

        if cid:
            where.append('u.consumable_id = %s')
            params.append(cid)
        if uid:
            where.append('u.user_id = %s')
            params.append(uid)
        if date_from:
            where.append('u.created_at >= %s')
            params.append(date_from)
        if date_to:
            where.append('u.created_at <= %s')
            params.append(date_to)
        if search:
            where.append('(c.name LIKE %s OR c.model LIKE %s OR users.name LIKE %s OR u.purpose LIKE %s)')
            kw = f"%{search}%"
            params.extend([kw, kw, kw, kw])

        base_sql = (
            "SELECT u.id, u.consumable_id, u.user_id, u.quantity, u.purpose, u.created_at, "
            "c.name AS consumable_name, c.model AS consumable_model, c.unit AS consumable_unit, c.unit_price AS consumable_unit_price, "
            "c.laboratory_id AS lab_id, l.name AS lab_name, users.name AS user_name "
            "FROM consumable_usage u "
            "LEFT JOIN consumables c ON u.consumable_id = c.id "
            "LEFT JOIN laboratories l ON c.laboratory_id = l.id "
            "LEFT JOIN users ON u.user_id = users.id "
        )
        if where:
            base_sql += ' WHERE ' + ' AND '.join(where)
        base_sql += ' ORDER BY u.created_at DESC, u.id DESC'

        result = execute_paginated_query(base_sql, tuple(params), page, page_size)
        if not result['success']:
            logger.error(f"查询耗材使用记录失败: {result.get('error')}")
            return error_response('获取耗材使用记录失败')

        items = []
        for r in result['data']:
            items.append({
                'id': r.get('id'),
                'consumableId': r.get('consumable_id'),
                'consumableName': r.get('consumable_name'),
                'consumableModel': r.get('consumable_model'),
                'userId': r.get('user_id'),
                'userName': r.get('user_name'),
                'labId': r.get('lab_id'),
                'labName': r.get('lab_name'),
                'unit': r.get('consumable_unit'),
                'unitPrice': float(r.get('consumable_unit_price') or 0),
                'quantity': float(r.get('quantity') or 0),
                'purpose': r.get('purpose'),
                'usageDate': r.get('created_at').date().isoformat() if r.get('created_at') else None,
                'createdAt': r.get('created_at').isoformat() if r.get('created_at') else None,
            })
        return paginated_response(items, result['pagination'], '获取耗材使用记录成功')
    except Exception as e:
        logger.error(f"获取耗材使用记录接口错误: {str(e)}")
        return error_response('获取耗材使用记录失败')

@consumables_bp.route('/usage/stats', methods=['GET'])
@require_auth
def consumable_usage_stats():
    try:
        by_month = execute_query(
            "SELECT DATE_FORMAT(created_at,'%Y-%m') AS ym, COUNT(*) AS cnt FROM consumable_usage GROUP BY ym ORDER BY ym DESC LIMIT 12"
        )
        top_consumables = execute_query(
            "SELECT c.name AS consumable_name, COUNT(u.id) AS cnt FROM consumable_usage u LEFT JOIN consumables c ON u.consumable_id = c.id GROUP BY c.id, c.name ORDER BY cnt DESC LIMIT 10"
        )
        top_users = execute_query(
            "SELECT users.name AS user_name, COUNT(u.id) AS cnt FROM consumable_usage u LEFT JOIN users ON u.user_id = users.id GROUP BY users.id, users.name ORDER BY cnt DESC LIMIT 10"
        )
        data = {
            'byMonth': [
                {'month': r.get('ym'), 'count': r.get('cnt')}
                for r in (by_month['data'] if by_month['success'] else [])
            ],
            'topConsumables': [
                {'name': r.get('consumable_name'), 'count': r.get('cnt')}
                for r in (top_consumables['data'] if top_consumables['success'] else [])
            ],
            'topUsers': [
                {'name': r.get('user_name'), 'count': r.get('cnt')}
                for r in (top_users['data'] if top_users['success'] else [])
            ]
        }
        return success_response(data, '获取耗材使用统计成功')
    except Exception as e:
        logger.error(f"耗材使用统计接口错误: {str(e)}")
        return error_response('获取耗材使用统计失败')

@consumables_bp.route('/usage/export', methods=['GET'])
@require_auth
def export_consumable_usage():
    try:
        sql = (
            "SELECT u.id, u.consumable_id, c.name AS consumable_name, c.model AS consumable_model, "
            "u.user_id, users.name AS user_name, u.quantity, c.unit AS unit, c.unit_price AS unit_price, "
            "u.created_at "
            "FROM consumable_usage u "
            "LEFT JOIN consumables c ON u.consumable_id = c.id "
            "LEFT JOIN users ON u.user_id = users.id "
            "ORDER BY u.created_at DESC, u.id DESC"
        )
        res = execute_query(sql)
        if not res['success']:
            return error_response('导出失败')
        rows = res['data'] or []
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID','耗材名称','型号','使用者','数量','单位','单价','使用日期'])
        for r in rows:
            writer.writerow([
                r.get('id'),
                r.get('consumable_name'),
                r.get('consumable_model'),
                r.get('user_name'),
                float(r.get('quantity') or 0),
                r.get('unit') or '',
                float(r.get('unit_price') or 0),
                (r.get('created_at').date().isoformat() if r.get('created_at') else '')
            ])
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=consumable_usage.csv'}
        )
    except Exception as e:
        logger.error(f"导出耗材使用记录接口错误: {str(e)}")
        return error_response('导出失败')