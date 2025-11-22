import sqlite3

# 连接到数据库
conn = sqlite3.connect('lab_management.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f'表名: {table[0]}')

print('\n' + '='*50)

# 查看课程表结构
if any('courses' in str(table) for table in tables):
    cursor.execute("PRAGMA table_info(courses)")
    columns = cursor.fetchall()
    print('课程表结构:')
    for col in columns:
        print(f'字段名: {col[1]}, 类型: {col[2]}, 允许为空: {col[3]}')
    
    print('\n' + '='*50)
    
    # 查看最新的几条课程记录
    cursor.execute("SELECT id, name, requires_lab, laboratory_id FROM courses ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    print('最新的课程记录:')
    for row in rows:
        print(f'ID: {row[0]}, Name: {row[1]}, Requires Lab: {row[2]}, Laboratory ID: {row[3]}')
else:
    print('没有找到courses表')

conn.close()