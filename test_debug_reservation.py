#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试预约创建失败的详细原因
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_reservation_creation():
    """测试预约创建并获取详细错误信息"""
    base_url = "http://localhost:3000/api"
    
    # 1. 登录获取token
    print("=== 调试预约创建失败原因 ===")
    print("1. 登录获取token...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.text}")
            return
            
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ 登录失败: {login_result.get('message')}")
            return
            
        token = login_result['data']['token']
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ 登录成功")
        
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 检查实验室状态
    print("\n2. 检查实验室状态...")
    try:
        response = requests.get(f"{base_url}/laboratories/1", headers=headers, timeout=10)
        print(f"实验室详情状态码: {response.status_code}")
        
        if response.status_code == 200:
            lab_result = response.json()
            print(f"实验室状态: {json.dumps(lab_result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 获取实验室详情失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 获取实验室详情异常: {e}")
    
    # 3. 检查时间冲突
    print("\n3. 检查时间冲突...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 先查询该时间段是否已有预约
    check_params = {
        "laboratory_id": 1,
        "date_from": tomorrow,
        "date_to": tomorrow
    }
    
    try:
        response = requests.get(f"{base_url}/reservations", params=check_params, headers=headers, timeout=10)
        print(f"预约查询状态码: {response.status_code}")
        
        if response.status_code == 200:
            reservations_result = response.json()
            existing_reservations = reservations_result.get('data', [])
            print(f"该时间段已有预约数量: {len(existing_reservations)}")
            
            for reservation in existing_reservations:
                print(f"  - 预约ID: {reservation['id']}, 时间: {reservation['reservation_date']} {reservation['start_time']}-{reservation['end_time']}")
        else:
            print(f"❌ 查询预约失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 查询预约异常: {e}")
    
    # 4. 尝试创建预约 - 逐步调试
    print(f"\n4. 尝试创建预约 ({tomorrow} 14:00-16:00)...")
    
    reservation_data = {
        "laboratory_id": 1,
        "reservation_date": tomorrow,
        "start_time": "14:00",
        "end_time": "16:00",
        "purpose": "调试测试预约",
        "equipment_ids": []
    }
    
    print(f"请求数据: {json.dumps(reservation_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/reservations", json=reservation_data, headers=headers, timeout=10)
        print(f"创建预约状态码: {response.status_code}")
        print(f"创建预约响应: {response.text}")
        
        if response.status_code != 201:
            print("❌ 预约创建失败")
            # 尝试获取更详细的错误信息
            try:
                error_result = response.json()
                print(f"错误详情: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
            except:
                print(f"原始响应: {response.text}")
        else:
            print("✅ 预约创建成功")
            result = response.json()
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        print(f"❌ 创建预约异常: {e}")

if __name__ == "__main__":
    test_reservation_creation()