#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为远程MySQL数据库运行迁移，添加requires_lab和laboratory_id字段
"""

import pymysql
import sys

def get_connection():
    """获取远程MySQL数据库连接"""
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

def get_existing_columns(table_name):
    """获取表的所有字段名"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [row[0] for row in cursor.fetchall()]
            return columns
    except Exception as e:
        print(f"❌ 获取表结构失败: {e}")
        return []
    finally:
        conn.close()

def migrate_courses_lab_fields():
    """为courses表添加requires_lab和laboratory_id字段"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # 获取现有字段
            cols = set(get_existing_columns('courses'))
            
            # 检查需要添加的字段
            if 'requires_lab' not in cols:
                print("正在添加requires_lab字段...")
                sql = """
                ALTER TABLE courses 
                ADD COLUMN `requires_lab` TINYINT(1) NOT NULL DEFAULT 0 
                COMMENT '是否需要实验室' 
                AFTER `semester`
                """
                cursor.execute(sql)
                print("✅ requires_lab字段添加成功")
            else:
                print("requires_lab字段已存在，跳过")
            
            if 'laboratory_id' not in cols:
                print("正在添加laboratory_id字段...")
                sql = """
                ALTER TABLE courses 
                ADD COLUMN `laboratory_id` INT NULL 
                COMMENT '关联实验室ID' 
                AFTER `requires_lab`
                """
                cursor.execute(sql)
                print("✅ laboratory_id字段添加成功")
            else:
                print("laboratory_id字段已存在，跳过")
            
            return True
            
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    finally:
        conn.close()

def verify_migration():
    """验证迁移结果"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("DESCRIBE courses")
            columns = cursor.fetchall()
            
            print("\n迁移后的courses表结构:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
            
            column_names = [col[0] for col in columns]
            
            if 'requires_lab' in column_names and 'laboratory_id' in column_names:
                print("\n✅ 迁移验证成功：所有字段都存在")
                return True
            else:
                print("\n❌ 迁移验证失败：字段缺失")
                return False
                
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== 运行远程MySQL数据库迁移 ===")
    
    success = migrate_courses_lab_fields()
    if success:
        print("\n迁移执行完成，正在验证...")
        verify_migration()
        print("\n✅ 数据库迁移完成")
    else:
        print("\n❌ 数据库迁移失败")
        sys.exit(1)