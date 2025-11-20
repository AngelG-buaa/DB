#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查实验室查询的具体结果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.init_database import execute_query

def check_lab_query():
    """检查实验室查询结果"""
    print("=== 检查实验室查询结果 ===")
    
    lab_check_sql = "SELECT id, name, status FROM laboratories WHERE id = %s"
    lab_result = execute_query(lab_check_sql, (1,))
    
    print(f"查询SQL: {lab_check_sql}")
    print(f"查询参数: (1,)")
    print(f"查询结果: {lab_result}")
    
    if lab_result['success'] and lab_result['data']:
        lab = lab_result['data'][0]
        print(f"实验室数据: {lab}")
        print(f"实验室状态: '{lab.get('status', 'NULL')}'")
        print(f"状态类型: {type(lab.get('status'))}")
        
        # 检查状态值
        if lab['status'] == 'available':
            print("✅ 实验室状态为available")
        elif lab['status'] == '':
            print("❌ 实验室状态为空字符串")
        elif lab['status'] is None:
            print("❌ 实验室状态为NULL")
        else:
            print(f"⚠️  实验室状态为: '{lab['status']}'")
    else:
        print("❌ 实验室查询失败或没有数据")

if __name__ == "__main__":
    check_lab_query()