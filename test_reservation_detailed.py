#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细测试创建预约API"""

import requests
import json

def test_create_reservation_detailed():
    """详细测试创建预约API"""
    base_url = "http://localhost:3000/api"
    
    print("=== 详细测试创建预约API ===")
    
    # 1. 先登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        print(f"登录状态码: {response.status_code}")
        login_result = response.json()
        print(f"登录响应: {json.dumps(login_result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and login_result.get('success'):
            token = login_result.get('data', {}).get('token')
            print(f"✅ 登录成功")
        else:
            print(f"❌ 登录失败: {login_result.get('message')}")
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
        print(f"实验室状态码: {response.status_code}")
        lab_result = response.json()
        print(f"实验室响应: {json.dumps(lab_result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and lab_result.get('success'):
            labs = lab_result.get('data', [])
            if labs:
                lab_id = labs[0]['id']
                lab_name = labs[0]['name']
                print(f"✅ 找到可用实验室: {lab_name} (ID: {lab_id})")
            else:
                print("❌ 没有找到可用实验室")
                return
        else:
            print(f"❌ 获取实验室失败: {lab_result.get('message')}")
            return
    except Exception as e:
        print(f"❌ 获取实验室异常: {e}")
        return
    
    # 3. 检查实验室详情
    print(f"\n3. 检查实验室 {lab_id} 详情...")
    try:
        response = requests.get(f"{base_url}/laboratories/{lab_id}", headers=headers, timeout=10)
        print(f"实验室详情状态码: {response.status_code}")
        lab_detail_result = response.json()
        print(f"实验室详情响应: {json.dumps(lab_detail_result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 获取实验室详情异常: {e}")
    
    # 4. 创建预约 - 尝试1: 不带设备
    print(f"\n4. 创建预约（不带设备）...")
    reservation_data = {
        "laboratory_id": lab_id,
        "reservation_date": "2025-11-27",
        "start_time": "14:00",
        "end_time": "16:00",
        "purpose": "API测试预约",
        "equipment_ids": []
    }
    
    print(f"请求数据: {json.dumps(reservation_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/reservations", json=reservation_data, headers=headers, timeout=10)
        print(f"创建预约状态码: {response.status_code}")
        create_result = response.json()
        print(f"创建预约响应: {json.dumps(create_result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201 and create_result.get('success'):
            print(f"✅ 预约创建成功！")
            reservation_id = create_result.get('data', {}).get('id')
            
            # 5. 验证预约是否真的创建成功
            print(f"\n5. 验证预约 {reservation_id} 是否存在于数据库...")
            verify_response = requests.get(f"{base_url}/reservations/{reservation_id}", headers=headers, timeout=10)
            print(f"验证状态码: {verify_response.status_code}")
            verify_result = verify_response.json()
            print(f"验证响应: {json.dumps(verify_result, ensure_ascii=False, indent=2)}")
            
            if verify_response.status_code == 200 and verify_result.get('success'):
                print(f"✅ 验证成功！预约确实存在于数据库中")
                
                # 6. 清理 - 删除测试预约
                print(f"\n6. 清理 - 删除测试预约 {reservation_id}...")
                delete_response = requests.delete(f"{base_url}/reservations/{reservation_id}", headers=headers, timeout=10)
                print(f"删除状态码: {delete_response.status_code}")
                delete_result = delete_response.json()
                print(f"删除响应: {json.dumps(delete_result, ensure_ascii=False, indent=2)}")
                
                if delete_response.status_code == 200 and delete_result.get('success'):
                    print(f"✅ 测试预约已成功删除")
                else:
                    print(f"⚠️  删除失败: {delete_result.get('message')}")
            else:
                print(f"❌ 验证失败！预约不存在于数据库中: {verify_result.get('message')}")
        else:
            print(f"❌ 预约创建失败: {create_result.get('message')}")
    except Exception as e:
        print(f"❌ 创建预约异常: {e}")

if __name__ == "__main__":
    test_create_reservation_detailed()