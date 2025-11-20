#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试实验室API响应格式"""

import requests

def test_lab_format():
    """测试实验室API响应格式"""
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
    
    # 获取所有实验室列表
    lab_response = requests.get(f"{base_url}/laboratories", headers=headers)
    print(f"状态码: {lab_response.status_code}")
    
    if lab_response.status_code == 200:
        result = lab_response.json()
        print(f"\n解析后的JSON:")
        print(f"success: {result.get('success')}")
        print(f"message: {result.get('message')}")
        
        # 检查data的结构
        data = result.get('data')
        if isinstance(data, list):
            print(f"找到 {len(data)} 个实验室")
            available_labs = [lab for lab in data if lab.get('status') == 'available']
            print(f"其中 {len(available_labs)} 个状态为available")
            
            if available_labs:
                print(f"第一个可用实验室: {available_labs[0]}")
            else:
                print("所有实验室:")
                for i, lab in enumerate(data):  # 显示所有实验室
                    print(f"  实验室{i+1}: {lab.get('name')} (状态: '{lab.get('status')}', ID: {lab.get('id')})")
        else:
            print(f"data是其他类型: {type(data)}")

if __name__ == "__main__":
    test_lab_format()