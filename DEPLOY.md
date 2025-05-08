# 失物招领系统生产环境部署指南

本文档提供了将失物招领系统部署到生产环境的详细步骤。

## 准备工作

### 系统要求
- Python 3.7+
- 支持HTTPS的Web服务器（推荐Nginx）
- 足够的存储空间用于上传的图片

### 安全注意事项
- 使用强密码和密钥
- 定期备份数据库
- 确保服务器安全更新

## 部署步骤

### 1. 准备环境变量

复制`.env.example`文件并创建`.env`文件：

```bash
cp .env.example .env
```

编辑`.env`文件，设置生产环境的配置：
- 设置强密码作为`SECRET_KEY`
- 配置管理员用户名和密码
- 设置数据库路径

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 使用Gunicorn运行应用

```bash
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app("production")'
```

参数说明：
- `-w 4`: 使用4个工作进程
- `-b 0.0.0.0:5000`: 绑定到所有网络接口的5000端口

### 5. 配置Nginx（推荐）

创建Nginx配置文件：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向HTTP到HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    # 安全头部
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static {
        alias /path/to/your/app/static;
        expires 30d;
    }
}
```

替换`your-domain.com`和证书路径为实际值。

### 6. 使用Systemd管理服务（可选）

创建服务文件`/etc/systemd/system/lostfound.service`：

```ini
[Unit]
Description=Lost and Found Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
EnvironmentFile=/path/to/your/app/.env
ExecStart=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5000 'app:create_app("production")'
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable lostfound
sudo systemctl start lostfound
```

## 维护

### 日志
应用日志位于`app.log`文件中，可以使用以下命令查看：

```bash
tail -f app.log
```

### 备份
定期备份数据库和上传的图片：

```bash
# 备份数据库
cp database.db database.db.backup-$(date +%Y%m%d)

# 备份上传的图片
tar -czf uploads-$(date +%Y%m%d).tar.gz static/uploads
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 安装依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart lostfound
```

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查日志文件`app.log`
   - 确认环境变量配置正确

2. **上传图片失败**
   - 检查`static/uploads`目录权限
   - 确认磁盘空间充足

3. **数据库错误**
   - 检查数据库文件权限
   - 尝试从备份恢复

### 联系支持

如有任何问题，请联系系统管理员。