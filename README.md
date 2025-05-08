# 失物招领网站

这是一个简单的失物招领网站，用户可以上传找到的物品和报告丢失的物品。

## 功能

- 用户可以上传找到的物品
- 用户可以报告丢失的物品
- 广场页面展示所有物品
- 点击物品可以查看详细信息
- 自动匹配丢失和找到的物品
- 管理员可以管理物品信息和状态

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python (Flask)
- 数据库：SQLite

## 安装和运行

### 开发环境

1. 安装依赖
```
pip install -r requirements.txt
```

2. 初始化数据库
```
python init_db.py
```

3. 运行应用
```
python app.py
```

4. 访问 http://localhost:5001

### 生产环境

1. 复制环境变量示例文件并修改
```
cp .env.example .env
# 编辑.env文件，设置适当的值
```

2. 使用生产环境启动脚本
```
./start_production.sh
```

详细的生产环境部署指南请参考 [DEPLOY.md](DEPLOY.md) 文件。