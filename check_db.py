#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库状态"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.init_database import execute_query

def check_database():
    """检查数据库状态"""
    print("=== 检查数据库状态 ===")
    
    # 检查所有实验室状态
    print("1. 检查实验室...")
    result = execute_query('SELECT id, name, status FROM laboratories')
    print(f'实验室查询结果: {result}')
    
    if result['success'] and result['data']:
        print(f"✅ 找到 {len(result['data'])} 个实验室:")
        for lab in result['data']:
            print(f"  - ID={lab['id']}, 名称={lab['name']}, 状态={lab['status']}")
    else:
        print(f"❌ 实验室查询失败: {result.get('error', '未知错误')}")
    
    # 检查用户
    print("\n2. 检查用户...")
    user_result = execute_query('SELECT id, name, role FROM users LIMIT 5')
    print(f'用户查询结果: {user_result}')
    
    if user_result['success'] and user_result['data']:
        print(f"✅ 找到用户:")
        for user in user_result['data']:
            print(f"  - ID={user['id']}, 名称={user['name']}, 角色={user['role']}")
    
    # 检查最近的预约
    print("\n3. 检查最近的预约...")
    reservation_result = execute_query('SELECT id, user_id, laboratory_id, purpose, status, created_at FROM reservations ORDER BY id DESC LIMIT 5')
    print(f'预约查询结果: {reservation_result}')
    
    if reservation_result['success'] and reservation_result['data']:
        print(f"✅ 找到 {len(reservation_result['data'])} 条预约记录:")
        for res in reservation_result['data']:
            print(f"  - ID={res['id']}, 用户ID={res['user_id']}, 实验室ID={res['laboratory_id']}, 目的={res['purpose']}, 状态={res['status']}, 创建时间={res['created_at']}")
    else:
        print(f"❌ 没有找到预约记录: {reservation_result.get('error', '无记录')}")

if __name__ == "__main__":
    check_database()