#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查远程MySQL数据库结构
用于验证courses表是否存在以及是否包含requires_lab和laboratory_id字段
"""

import pymysql
import sys

def get_connection():
    """获取远程MySQL数据库连接（与init_database.py配置相同）"""
    try:
        return pymysql.connect(
            host="124.70.86.207",
            port=3306,
            user="u23373478",
            password="Aa614026",
            database="h_db23373478",
            charset='utf8',
            autocommit=True
        )
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def check_database_structure():
    """检查数据库结构"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # 检查所有表
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"数据库中的表: {tables}")
            
            if 'courses' not in tables:
                print("❌ courses表不存在")
                return False
            
            print("✅ courses表存在")
            
            # 检查courses表结构
            cursor.execute("DESCRIBE courses")
            columns = cursor.fetchall()
            
            print("\ncourses表结构:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
            
            # 检查是否包含所需字段
            column_names = [col[0] for col in columns]
            
            if 'requires_lab' not in column_names:
                print("❌ requires_lab字段不存在")
                return False
            else:
                print("✅ requires_lab字段存在")
            
            if 'laboratory_id' not in column_names:
                print("❌ laboratory_id字段不存在")
                return False
            else:
                print("✅ laboratory_id字段存在")
            
            # 检查现有数据
            cursor.execute("SELECT COUNT(*) FROM courses")
            course_count = cursor.fetchone()[0]
            print(f"\n课程总数: {course_count}")
            
            if course_count > 0:
                cursor.execute("SELECT id, name, requires_lab, laboratory_id FROM courses ORDER BY id DESC LIMIT 5")
                recent_courses = cursor.fetchall()
                print("\n最近的5个课程:")
                for course in recent_courses:
                    print(f"  ID: {course[0]}, 名称: {course[1]}, 需要实验室: {course[2]}, 实验室ID: {course[3]}")
            
            return True
            
    except Exception as e:
        print(f"❌ 查询数据库时出错: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== 检查远程MySQL数据库结构 ===")
    success = check_database_structure()
    if success:
        print("\n✅ 数据库结构检查完成")
    else:
        print("\n❌ 数据库结构检查失败")
        sys.exit(1)