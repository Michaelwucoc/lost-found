import sqlite3
import os

# 确保数据库目录存在
os.makedirs('static/uploads', exist_ok=True)

# 连接到数据库（如果不存在则创建）
connection = sqlite3.connect('database.db')

# 获取游标
cursor = connection.cursor()

# 创建物品表
cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- 'lost' 或 'found'
    name_cn TEXT NOT NULL,  -- 报告人中文姓名
    name_en TEXT NOT NULL,  -- 报告人英文姓名
    location TEXT NOT NULL,  -- 丢失/找到地点
    description TEXT,  -- 物品描述
    image TEXT,  -- 图片文件名
    created_at TEXT NOT NULL,  -- 创建时间
    matched INTEGER DEFAULT 0  -- 是否已匹配
)
''')

# 创建匹配表
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    matched_item_id TEXT NOT NULL,
    matched_at TEXT NOT NULL,  -- 匹配时间
    FOREIGN KEY (item_id) REFERENCES items (id),
    FOREIGN KEY (matched_item_id) REFERENCES items (id)
)
''')

# 提交更改并关闭连接
connection.commit()
connection.close()

print('数据库初始化完成！')