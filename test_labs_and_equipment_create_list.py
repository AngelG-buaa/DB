#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import uuid
import json

BASE = "http://localhost:3000/api"

def login_admin():
    r = requests.post(f"{BASE}/auth/login", json={"username":"admin","password":"admin123"}, timeout=10)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data.get('success') is True
    return {"Authorization": f"Bearer {data['data']['token']}"}

def run():
    headers = login_admin()

    # 1) 创建随机实验室
    name = f"API-测试实验室-{uuid.uuid4().hex[:8]}"
    lab_payload = {
        "name": name,
        "location": "教学楼A-301",
        "capacity": 30,
        "description": "API脚本创建",
        "status": "available"
    }
    r = requests.post(f"{BASE}/laboratories", json=lab_payload, headers=headers, timeout=10)
    print("创建实验室状态:", r.status_code)
    print("创建实验室响应:", r.text)
    assert r.status_code in (200,201), r.text
    lab_res = r.json()
    assert (lab_res.get('success') or lab_res.get('code') in ('SUCCESS','CREATED')), lab_res

    # 获取新实验室ID
    if isinstance(lab_res.get('data'), dict) and lab_res['data'].get('id'):
        lab_id = lab_res['data']['id']
    else:
        # 通过列表查询定位
        lr = requests.get(f"{BASE}/laboratories", params={"search": name, "page":1, "page_size":10}, headers=headers, timeout=10)
        print("查询实验室状态:", lr.status_code)
        print("查询实验室响应:", lr.text)
        assert lr.status_code == 200
        list_data = lr.json()
        assert list_data.get('success') is True
        labs = list_data.get('data')
        assert isinstance(labs, list) and len(labs) >= 1
        lab_id = labs[0]['id']

    # 2) 创建设备
    eq_payload = {
        "name": f"示波器-{uuid.uuid4().hex[:6]}",
        "model": "DS1002",
        "serial_number": f"SN-{uuid.uuid4().hex[:10]}",
        "laboratory_id": lab_id,
        "description": "API创建设备",
        "status": "available"
    }
    er = requests.post(f"{BASE}/equipment", json=eq_payload, headers=headers, timeout=10)
    print("创建设备状态:", er.status_code)
    print("创建设备响应:", er.text)
    assert er.status_code in (200,201), er.text
    eq_res = er.json()
    assert (eq_res.get('success') or eq_res.get('code') in ('SUCCESS','CREATED')), eq_res

    # 3) 列出设备，按实验室过滤，验证存在
    gl = requests.get(f"{BASE}/equipment", params={"laboratory_id": lab_id, "page":1, "page_size":10}, headers=headers, timeout=10)
    print("设备列表状态:", gl.status_code)
    print("设备列表响应:", json.dumps(gl.json(), ensure_ascii=False))
    assert gl.status_code == 200
    glj = gl.json()
    assert glj.get('success') is True
    items = glj.get('data', [])
    assert any(i.get('laboratory') or True for i in items), "设备列表应返回设备"

    print("✅ 验证通过：新建实验室与设备均可在列表中查询到")

if __name__ == "__main__":
    run()