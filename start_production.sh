#!/bin/bash

# 生产环境启动脚本

# 检查.env文件是否存在
if [ ! -f .env ]; then
    echo "错误：.env文件不存在，请先从.env.example创建"
    echo "可以使用命令：cp .env.example .env 然后编辑.env文件"
    exit 1
fi

# 加载环境变量
set -a
source .env
set +a

echo "正在安装依赖..."
pip install -r requirements.txt

echo "正在初始化数据库..."
python init_db.py

echo "启动应用服务器..."
if command -v gunicorn &> /dev/null; then
    # 使用gunicorn启动
    gunicorn -w 4 -b ${HOST:-0.0.0.0}:${PORT:-5000} "app:create_app('production')"
else
    echo "警告：未找到gunicorn，使用Flask内置服务器启动（不推荐用于生产环境）"
    python app.py
fi