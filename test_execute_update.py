#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试execute_update函数来调试预约创建失败原因
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.init_database import execute_update, execute_query
from datetime import datetime, timedelta

def test_execute_update():
    """测试execute_update函数"""
    print("=== 测试execute_update函数 ===")
    
    # 测试参数
    user_id = 1
    laboratory_id = 1
    reservation_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    start_time = "14:00"
    end_time = "16:00"
    purpose = "直接测试execute_update"
    equipment_ids_str = ""
    status = "confirmed"
    
    print(f"测试参数:")
    print(f"  user_id: {user_id}")
    print(f"  laboratory_id: {laboratory_id}")
    print(f"  reservation_date: {reservation_date}")
    print(f"  start_time: {start_time}")
    print(f"  end_time: {end_time}")
    print(f"  purpose: {purpose}")
    print(f"  equipment_ids_str: '{equipment_ids_str}'")
    print(f"  status: {status}")
    
    # 测试SQL语句
    insert_sql = """
    INSERT INTO reservations (user_id, laboratory_id, reservation_date, start_time, 
                            end_time, purpose, equipment_ids, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    
    print(f"\nSQL语句: {insert_sql}")
    
    params = (user_id, laboratory_id, reservation_date, start_time,
              end_time, purpose, equipment_ids_str, status)
    
    print(f"参数元组: {params}")
    
    # 执行更新
    print("\n执行execute_update...")
    result = execute_update(insert_sql, params)
    
    print(f"执行结果: {result}")
    
    if result['success']:
        print(f"✅ 执行成功！last_insert_id: {result.get('last_insert_id')}")
        
        # 验证数据是否真的插入
        verify_sql = "SELECT * FROM reservations WHERE id = %s"
        verify_result = execute_query(verify_sql, (result['last_insert_id'],))
        
        if verify_result['success'] and verify_result['data']:
            print("✅ 数据验证成功 - 记录确实存在于数据库中")
            print(f"插入的记录: {verify_result['data'][0]}")
            
            # 清理测试数据
            delete_sql = "DELETE FROM reservations WHERE id = %s"
            delete_result = execute_update(delete_sql, (result['last_insert_id'],))
            
            if delete_result['success']:
                print("✅ 测试数据已清理")
            else:
                print(f"⚠️  清理数据失败: {delete_result.get('error')}")
        else:
            print("❌ 数据验证失败 - 记录不存在于数据库中")
            
    else:
        print(f"❌ 执行失败: {result.get('error')}")
        print(f"错误详情: {result}")

if __name__ == "__main__":
    test_execute_update()