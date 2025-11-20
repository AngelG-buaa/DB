#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新实验室状态为可用"""

import requests

def update_lab_status():
    """更新实验室状态为可用"""
    base_url = "http://localhost:3000/api"
    
    # 登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    login_result = login_response.json()
    if not login_result.get('success'):
        print(f"登录失败: {login_result.get('message')}")
        return
    
    token = login_result.get('data', {}).get('token')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 更新第一个实验室状态为available
    lab_id = 1  # 计算机实验室A
    update_data = {
        "status": "available"
    }
    
    print(f"更新实验室 {lab_id} 状态为available...")
    response = requests.put(f"{base_url}/laboratories/{lab_id}", json=update_data, headers=headers)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {result}")
    
    if response.status_code == 200 and result.get('success'):
        print("✅ 实验室状态更新成功！")
    else:
        print(f"❌ 更新失败: {result.get('message')}")

if __name__ == "__main__":
    update_lab_status()