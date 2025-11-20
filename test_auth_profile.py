#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def run():
    base_url = "http://localhost:3000/api"
    login = requests.post(f"{base_url}/auth/login", json={"username":"admin","password":"admin123"}, timeout=10)
    assert login.status_code == 200, f"login failed: {login.text}"
    token = login.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    prof = requests.get(f"{base_url}/auth/profile", headers=headers, timeout=10)
    print("profile status:", prof.status_code)
    print("profile:", prof.text)

if __name__ == "__main__":
    run()