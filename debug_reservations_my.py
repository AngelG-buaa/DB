#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from backend.init_database import execute_paginated_query, execute_query

def main():
    # 获取任意一个用户ID用于模拟当前用户
    u = execute_query("SELECT id, username FROM users ORDER BY id LIMIT 1")
    print("users query:", json.dumps(u, ensure_ascii=False))
    uid = None
    if u['success'] and u['data']:
        uid = u['data'][0]['id']
    else:
        print("无法获取用户ID")
        return

    base_sql = (
        "SELECT r.id, r.reservation_date, r.start_time, r.end_time, r.purpose, "
        "r.status, r.equipment_ids, r.created_at, r.updated_at, "
        "l.name as laboratory_name, l.location as laboratory_location "
        "FROM reservations r "
        "JOIN laboratories l ON r.laboratory_id = l.id "
        "WHERE r.user_id = %s "
        "ORDER BY r.reservation_date DESC, r.start_time DESC"
    )

    res = execute_paginated_query(base_sql, (uid,), page=1, page_size=5)
    print("execute_paginated_query:", json.dumps(res, ensure_ascii=False, default=str))
    with open('debug_out.txt','w',encoding='utf-8') as f:
        f.write("users query:\n")
        f.write(json.dumps(u, ensure_ascii=False, default=str))
        f.write("\nexecute_paginated_query:\n")
        f.write(json.dumps(res, ensure_ascii=False, default=str))

if __name__ == '__main__':
    main()