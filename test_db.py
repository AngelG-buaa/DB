#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试数据库连接和操作"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.init_database import execute_update, execute_query

def test_database_operations():
    """测试数据库操作"""
    print("=== 开始测试数据库操作 ===")
    
    # 首先检查是否存在有效的用户和实验室
    print("0. 检查测试数据...")
    user_check = execute_query("SELECT id FROM users LIMIT 1")
    lab_check = execute_query("SELECT id FROM laboratories WHERE status = 'available' LIMIT 1")
    
    print(f"用户检查结果: {user_check}")
    print(f"实验室检查结果: {lab_check}")
    
    if not user_check['success'] or not user_check['data']:
        print("❌ 没有找到有效用户，无法继续测试")
        return
        
    if not lab_check['success'] or not lab_check['data']:
        print("❌ 没有找到可用实验室，无法继续测试")
        return
    
    test_user_id = user_check['data'][0]['id']
    test_lab_id = lab_check['data'][0]['id']
    print(f"使用用户ID: {test_user_id}, 实验室ID: {test_lab_id}")
    
    # 测试插入数据
    print("\n1. 测试插入数据...")
    test_sql = """
    INSERT INTO reservations (user_id, laboratory_id, reservation_date, start_time, 
                           end_time, purpose, status, created_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    result = execute_update(test_sql, (test_user_id, test_lab_id, '2025-01-20', '10:00', '12:00', '测试预约', 'pending'))
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
            print(f"记录详情: ID={query_result['data'][0]['id']}, 目的={query_result['data'][0]['purpose']}")
            
            # 删除测试数据
            print("\n3. 测试删除数据...")
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
    test_database_operations()