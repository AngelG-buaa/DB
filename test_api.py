#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试后端API调用"""

import requests
import json

def test_api():
    """测试后端API"""
    base_url = "http://localhost:3000/api"
    
    print("=== 测试后端API ===")
    
    # 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"健康检查响应: {response.json()}")
        else:
            print(f"健康检查失败: {response.text}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 测试登录
    print("\n2. 测试登录...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        print(f"登录状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"登录响应: {result}")
            if result.get('success'):
                token = result.get('data', {}).get('token')
                print(f"✅ 登录成功，获取token: {token[:20]}...")
                return token
        else:
            print(f"登录失败: {response.text}")
    except Exception as e:
        print(f"❌ 登录异常: {e}")
    
    return None

def test_reservation_api(token):
    """测试预约API"""
    base_url = "http://localhost:3000/api"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n3. 测试预约列表...")
    try:
        response = requests.get(f"{base_url}/reservations", headers=headers, timeout=10)
        print(f"预约列表状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"预约列表完整响应: {result}")
            if isinstance(result, dict) and result.get('data'):
                data = result.get('data', {})
                if isinstance(data, dict):
                    reservation_list = data.get('list', [])
                    print(f"✅ 预约列表成功，找到 {len(reservation_list)} 条记录")
                else:
                    print(f"✅ 预约列表成功，数据格式: {type(data)}")
            else:
                print(f"✅ 预约列表成功，响应格式: {type(result)}")
        else:
            print(f"预约列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 预约列表异常: {e}")

if __name__ == "__main__":
    token = test_api()
    if token:
        test_reservation_api(token)