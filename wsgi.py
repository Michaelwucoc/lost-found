from app import create_app

# 创建应用实例，用于Gunicorn启动
application = create_app('production')

if __name__ == '__main__':
    application.run()