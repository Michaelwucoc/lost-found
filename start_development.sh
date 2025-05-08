#!/bin/bash

# 开发环境启动脚本

# 检查.env文件是否存在，如果不存在则从示例创建
if [ ! -f .env ]; then
    echo "提示：.env文件不存在，正在从.env.example创建"
    cp .env.example .env
    echo "已创建.env文件，请根据需要编辑配置"
fi

# 加载环境变量
set -a
source .env
# 设置为开发环境
export FLASK_ENV=development
set +a

echo "正在安装依赖..."
pip3 install -r requirements.txt --break-system-packages

echo "正在初始化数据库..."
python3 init_db.py

echo "启动开发服务器..."
# 使用Flask内置服务器启动开发环境，不需要SSL
export FLASK_ENV=development
export FLASK_APP=app.py
python3 app.py