#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试数据库操作（使用真实数据）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.init_database import execute_update, execute_query

def test_real_database_operations():
    """使用真实数据测试数据库操作"""
    print("=== 使用真实数据测试数据库操作 ===")
    
    # 获取第一个用户和实验室
    user_result = execute_query("SELECT id, name FROM users LIMIT 1")
    lab_result = execute_query("SELECT id, name FROM laboratories LIMIT 1")
    
    if not user_result['success'] or not user_result['data']:
        print("❌ 没有找到用户")
        return
        
    if not lab_result['success'] or not lab_result['data']:
        print("❌ 没有找到实验室")
        return
    
    user_id = user_result['data'][0]['id']
    lab_id = lab_result['data'][0]['id']
    
    print(f"使用用户ID: {user_id}, 实验室ID: {lab_id}")
    
    # 测试插入数据
    print("\n1. 测试插入数据...")
    test_sql = """
    INSERT INTO reservations (user_id, laboratory_id, reservation_date, start_time, 
                           end_time, purpose, status, created_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    result = execute_update(test_sql, (user_id, lab_id, '2025-01-20', '10:00', '12:00', '测试预约', 'pending'))
    print(f'插入结果: {result}')
    
    if result['success']:
        print(f"✅ 插入成功，影响行数: {result['affected_rows']}, 最后插入ID: {result['last_insert_id']}")
        
        # 查询刚才插入的数据
        print("\n2. 测试查询数据...")
        select_sql = 'SELECT * FROM reservations WHERE id = %s'
        query_result = execute_query(select_sql, (result['last_insert_id'],))
        print(f'查询结果: {query_result}')
        
        if query_result['success'] and query_result['data']:
            print(f"✅ 查询成功，找到 {len(query_result['data'])} 条记录")
            res = query_result['data'][0]
            print(f"记录详情: ID={res['id']}, 用户ID={res['user_id']}, 实验室ID={res['laboratory_id']}, 目的={res['purpose']}, 状态={res['status']}, 创建时间={res['created_at']}")
            
            # 测试更新数据
            print("\n3. 测试更新数据...")
            update_sql = 'UPDATE reservations SET purpose = %s WHERE id = %s'
            update_result = execute_update(update_sql, ('更新后的测试预约', result['last_insert_id']))
            print(f'更新结果: {update_result}')
            
            if update_result['success']:
                print(f"✅ 更新成功，影响行数: {update_result['affected_rows']}")
                
                # 验证更新
                verify_result = execute_query('SELECT purpose FROM reservations WHERE id = %s', (result['last_insert_id'],))
                if verify_result['success'] and verify_result['data']:
                    print(f"验证更新: 新目的 = {verify_result['data'][0]['purpose']}")
            else:
                print(f"❌ 更新失败: {update_result.get('error', '未知错误')}")
            
            # 删除测试数据
            print("\n4. 测试删除数据...")
            delete_sql = 'DELETE FROM reservations WHERE id = %s'
            delete_result = execute_update(delete_sql, (result['last_insert_id'],))
            print(f'删除结果: {delete_result}')
            
            if delete_result['success']:
                print(f"✅ 删除成功，影响行数: {delete_result['affected_rows']}")
            else:
                print(f"❌ 删除失败: {delete_result.get('error', '未知错误')}")
        else:
            print(f"❌ 查询失败或没有找到数据: {query_result.get('error', '未知错误')}")
    else:
        print(f"❌ 插入失败: {result.get('error', '未知错误')}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_real_database_operations()