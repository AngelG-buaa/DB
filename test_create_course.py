#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试创建课程API"""

import requests
import json
import time

def test_create_course():
    """测试创建课程API"""
    base_url = "http://localhost:3000/api"
    
    print("=== 测试创建课程API ===")
    
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
    
    # 2. 获取可用的教师
    print("\n2. 获取可用教师...")
    teacher_id = None
    try:
        response = requests.get(f"{base_url}/users?role=teacher&page_size=10", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('data') and isinstance(result['data'], list) and result['data']:
                teachers = result['data']
                if teachers:
                    teacher_id = teachers[0]['id']
                    teacher_name = teachers[0].get('name') or teachers[0].get('username')
                    print(f"✅ 找到可用教师: {teacher_name} (ID: {teacher_id})")
                else:
                    print("❌ 没有找到可用教师")
                    return
            else:
                print("❌ 教师列表格式异常")
                return
        else:
            print(f"❌ 获取教师失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取教师异常: {e}")
        return
    
    # 3. 获取可用的实验室
    print("\n3. 获取可用实验室...")
    lab_id = None
    lab_name = None
    try:
        response = requests.get(f"{base_url}/laboratories?status=available", headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('data') and isinstance(result['data'], list):
                labs = result['data']
                if labs:
                    lab_id = labs[0]['id']
                    lab_name = labs[0]['name']
                    print(f"✅ 找到可用实验室: {lab_name} (ID: {lab_id})")
                else:
                    print("⚠️ 没有找到可用实验室，将创建不需要实验室的课程")
            else:
                print("❌ 实验室列表格式异常")
                return
        else:
            print(f"❌ 获取实验室失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取实验室异常: {e}")
        return
    
    # 4. 创建需要实验室的课程
    print("\n4. 创建需要实验室的课程...")
    course_data = {
        "name": "测试课程-需要实验室",
        "code": f"TEST{int(time.time())}",
        "description": "这是一个测试课程，需要实验室",
        "credits": 3,
        "semester": "2025春",
        "teacher_id": teacher_id,
        "status": "active",
        "requires_lab": 1,  # 需要实验室
        "laboratory_id": lab_id  # 关联实验室
    }
    
    try:
        response = requests.post(f"{base_url}/courses", json=course_data, headers=headers, timeout=10)
        print(f"创建课程状态码: {response.status_code}")
        result = response.json()
        print(f"创建课程响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201 and result.get('success'):
            print(f"✅ 课程创建成功！")
            course_id = result.get('data', {}).get('id')
            
            # 5. 验证课程是否真的创建成功并包含实验室信息
            print("\n5. 验证课程是否存在于数据库并包含实验室信息...")
            verify_response = requests.get(f"{base_url}/courses/{course_id}", headers=headers, timeout=10)
            if verify_response.status_code == 200:
                verify_result = verify_response.json()
                if verify_result.get('success'):
                    course_data = verify_result.get('data', {})
                    print(f"✅ 验证成功！课程详情: {json.dumps(course_data, ensure_ascii=False, indent=2)}")
                    
                    # 检查requires_lab和laboratory_name是否正确
                    requires_lab = course_data.get('requires_lab')
                    laboratory_name = course_data.get('laboratory_name')
                    
                    if requires_lab is True:
                        print("✅ requires_lab字段正确 (True)")
                    else:
                        print(f"❌ requires_lab字段错误: 期望True, 实际{requires_lab}")
                    
                    if laboratory_name:
                        print(f"✅ laboratory_name字段正确: {laboratory_name}")
                    else:
                        print(f"❌ laboratory_name字段错误: 期望有值, 实际{laboratory_name}")
                else:
                    print(f"❌ 验证失败！课程不存在或获取详情失败")
            else:
                print(f"❌ 验证请求失败: {verify_response.status_code}")
                
            # 6. 清理测试数据
            print("\n6. 清理测试数据...")
            delete_response = requests.delete(f"{base_url}/courses/{course_id}", headers=headers, timeout=10)
            if delete_response.status_code == 200:
                print(f"✅ 测试数据清理成功")
            else:
                print(f"❌ 测试数据清理失败: {delete_response.status_code}")
                
        else:
            print(f"❌ 课程创建失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 创建课程异常: {e}")

if __name__ == "__main__":
    test_create_course()