#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试创建预约API"""

import requests
import json

def test_create_reservation():
    """测试创建预约API"""
    base_url = "http://localhost:3000/api"
    
    print("=== 测试创建预约API ===")
    
    # 1. 先登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print(f"✅ 登录成功")
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. 获取可用的实验室
    print("\n2. 获取可用实验室...")
    try:
        response = requests.get(f"{base_url}/laboratories?status=available", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('data') and isinstance(result['data'], list):
                labs = result['data']
                if labs:
                    lab_id = labs[0]['id']
                    print(f"✅ 找到可用实验室: {labs[0]['name']} (ID: {lab_id})")
                else:
                    print("❌ 没有找到可用实验室")
                    return
            else:
                print("❌ 实验室列表格式异常")
                return
        else:
            print(f"❌ 获取实验室失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取实验室异常: {e}")
        return
    
    # 3. 创建预约
    print("\n3. 创建预约...")
    reservation_data = {
        "laboratory_id": lab_id,
        "reservation_date": "2025-11-27",
        "start_time": "14:00",
        "end_time": "16:00",
        "purpose": "API测试预约",
        "equipment_ids": []
    }
    
    try:
        response = requests.post(f"{base_url}/reservations", json=reservation_data, headers=headers, timeout=10)
        print(f"创建预约状态码: {response.status_code}")
        result = response.json()
        print(f"创建预约响应: {result}")
        
        if response.status_code == 201 and result.get('success'):
            print(f"✅ 预约创建成功！")
            reservation_id = result.get('data', {}).get('id')
            
            # 4. 验证预约是否真的创建成功
            print("\n4. 验证预约是否存在于数据库...")
            verify_response = requests.get(f"{base_url}/reservations/{reservation_id}", headers=headers, timeout=10)
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                if verify_result.get('success'):
                    print(f"✅ 验证成功！预约确实存在于数据库中")
                    print(f"预约详情: {verify_result.get('data')}")
                else:
                    print(f"❌ 验证失败！预约不存在于数据库中")
            else:
                print(f"❌ 验证请求失败: {verify_response.status_code}")
                
            # 5. 清理测试数据
            print("\n5. 清理测试数据...")
            delete_response = requests.delete(f"{base_url}/reservations/{reservation_id}", headers=headers, timeout=10)
            if delete_response.status_code == 200:
                print(f"✅ 测试数据清理成功")
            else:
                print(f"❌ 测试数据清理失败: {delete_response.status_code}")
                
        else:
            print(f"❌ 预约创建失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 创建预约异常: {e}")

if __name__ == "__main__":
    test_create_reservation()