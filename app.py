from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
from datetime import datetime
import uuid
import logging
from werkzeug.utils import secure_filename
from config import config as app_config

# 创建应用并加载配置
def create_app(config_name='production'):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    
    # 从环境变量获取 secret key
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 配置日志
    if not app.debug:
        handler = logging.FileHandler('app.log')
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
    
    return app

# 根据环境变量选择配置，默认为生产环境
app = create_app(os.environ.get('FLASK_ENV') or 'production')

# 如果是开发环境，确保不需要HTTPS
if os.environ.get('FLASK_ENV') == 'development':
    app.config['SESSION_COOKIE_SECURE'] = False

# 数据库连接
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 主页 - 广场页面
@app.route('/')
def index():
    conn = get_db_connection()
    # 获取所有丢失物品，未匹配的在前，已匹配的在后
    lost_items = conn.execute(
        "SELECT * FROM items WHERE type='lost' ORDER BY matched ASC, created_at DESC"
    ).fetchall()
    # 获取所有找到物品，未匹配的在前，已匹配的在后
    found_items = conn.execute(
        "SELECT * FROM items WHERE type='found' ORDER BY matched ASC, created_at DESC"
    ).fetchall()
    conn.close()
    return render_template('index.html', lost_items=lost_items, found_items=found_items)

# 物品详情页面
@app.route('/item/<item_id>')
def item_detail(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    # 如果物品已匹配，获取匹配的物品
    matched_item = None
    if item and item['matched'] == 1:
        matched_id = conn.execute(
            'SELECT matched_item_id FROM matches WHERE item_id = ?', 
            (item_id,)
        ).fetchone()
        if matched_id:
            matched_item = conn.execute(
                'SELECT * FROM items WHERE id = ?', 
                (matched_id['matched_item_id'],)
            ).fetchone()
    
    conn.close()
    if item:
        return render_template('item_detail.html', item=item, matched_item=matched_item)
    flash('物品不存在')
    return redirect(url_for('index'))

# 报告丢失物品
@app.route('/report/lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        name_cn = request.form['name_cn']
        name_en = request.form['name_en']
        location = request.form['location']
        description = request.form['description']
        
        # 处理图片上传
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 使用UUID生成唯一文件名
                image_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # 如果没有描述也没有图片，且不是管理员，返回错误
        if not description and not image_filename and not session.get('admin'):
            flash('请提供物品描述或上传图片')
            return redirect(url_for('report_lost'))
        
        # 保存到数据库
        conn = get_db_connection()
        item_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO items (id, type, name_cn, name_en, location, description, image, created_at, matched) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (item_id, 'lost', name_cn, name_en, location, description, image_filename, datetime.now().isoformat(), 0)
        )
        conn.commit()
        
        # 查找可能匹配的找到物品
        potential_matches = conn.execute(
            "SELECT * FROM items WHERE type='found' AND matched=0"
        ).fetchall()
        conn.close()
        
        if potential_matches:
            return render_template('potential_matches.html', item_id=item_id, matches=potential_matches, item_type='lost')
        
        flash('物品丢失信息已记录')
        return redirect(url_for('index'))
    
    return render_template('report_lost.html')

# 报告找到物品
@app.route('/report/found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        name_cn = request.form['name_cn']
        name_en = request.form['name_en']
        location = request.form['location']
        description = request.form['description']
        
        # 处理图片上传
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 使用UUID生成唯一文件名
                image_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # 如果没有描述也没有图片，且不是管理员，返回错误
        if not description and not image_filename and not session.get('admin'):
            flash('请提供物品描述或上传图片')
            return redirect(url_for('report_found'))
        
        # 保存到数据库
        conn = get_db_connection()
        item_id = str(uuid.uuid4())
        conn.execute(
            'INSERT INTO items (id, type, name_cn, name_en, location, description, image, created_at, matched) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (item_id, 'found', name_cn, name_en, location, description, image_filename, datetime.now().isoformat(), 0)
        )
        conn.commit()
        
        # 查找可能匹配的丢失物品
        potential_matches = conn.execute(
            "SELECT * FROM items WHERE type='lost' AND matched=0"
        ).fetchall()
        conn.close()
        
        if potential_matches:
            return render_template('potential_matches.html', item_id=item_id, matches=potential_matches, item_type='found')
        
        flash('物品找到信息已记录')
        return redirect(url_for('index'))
    
    return render_template('report_found.html')

# 确认匹配
@app.route('/confirm_match/<item_id>/<matched_item_id>')
def confirm_match(item_id, matched_item_id):
    conn = get_db_connection()
    
    # 更新两个物品的匹配状态
    conn.execute('UPDATE items SET matched = 1 WHERE id = ?', (item_id,))
    conn.execute('UPDATE items SET matched = 1 WHERE id = ?', (matched_item_id,))
    
    # 记录匹配关系
    conn.execute(
        'INSERT INTO matches (item_id, matched_item_id, matched_at) VALUES (?, ?, ?)',
        (item_id, matched_item_id, datetime.now().isoformat())
    )
    conn.execute(
        'INSERT INTO matches (item_id, matched_item_id, matched_at) VALUES (?, ?, ?)',
        (matched_item_id, item_id, datetime.now().isoformat())
    )
    
    conn.commit()
    conn.close()
    
    flash('物品已成功匹配！')
    return redirect(url_for('index'))

# 管理员登录
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 从环境变量获取管理员凭据，提高安全性
        admin_user = os.environ.get('ADMIN_USERNAME') or 'admin'
        admin_pass = os.environ.get('ADMIN_PASSWORD') or 'Michael00900!!'
        
        if username == admin_user and password == admin_pass:
            session['admin'] = True
            session.permanent = True  # 使用永久会话，但有过期时间
            app.logger.info(f'管理员登录成功: {username}')
            flash('管理员登录成功')
            return redirect(url_for('admin_dashboard'))
        else:
            app.logger.warning(f'管理员登录失败: {username}')
            flash('用户名或密码错误')
    
    return render_template('admin_login.html')

# 管理员面板
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        flash('请先登录')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', items=items)

# 管理员编辑物品
@app.route('/admin/edit/<item_id>', methods=['GET', 'POST'])
def admin_edit(item_id):
    if not session.get('admin'):
        flash('请先登录')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    
    if request.method == 'POST':
        name_cn = request.form['name_cn']
        name_en = request.form['name_en']
        location = request.form['location']
        description = request.form['description']
        matched = 1 if 'matched' in request.form else 0
        
        # 处理图片上传
        image_filename = item['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 使用UUID生成唯一文件名
                image_filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # 更新数据库
        conn.execute(
            'UPDATE items SET name_cn = ?, name_en = ?, location = ?, description = ?, image = ?, matched = ? WHERE id = ?',
            (name_cn, name_en, location, description, image_filename, matched, item_id)
        )
        conn.commit()
        conn.close()
        
        flash('物品信息已更新')
        return redirect(url_for('admin_dashboard'))
    
    conn.close()
    return render_template('admin_edit.html', item=item)

# 管理员删除物品
@app.route('/admin/delete/<item_id>')
def admin_delete(item_id):
    if not session.get('admin'):
        flash('请先登录')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    
    # 获取物品信息以删除图片
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if item and item['image']:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item['image']))
        except:
            pass  # 如果图片不存在，忽略错误
    
    # 删除匹配记录
    conn.execute('DELETE FROM matches WHERE item_id = ? OR matched_item_id = ?', (item_id, item_id))
    
    # 删除物品
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    
    conn.commit()
    conn.close()
    
    flash('物品已删除')
    return redirect(url_for('admin_dashboard'))

# 管理员登出
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('已登出')
    return redirect(url_for('index'))

# 搜索功能
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    item_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    
    conn = get_db_connection()
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    # 关键词搜索（姓名或描述）
    if keyword:
        query += " AND (name_cn LIKE ? OR name_en LIKE ? OR description LIKE ?)"
        keyword_param = f'%{keyword}%'
        params.extend([keyword_param, keyword_param, keyword_param])
    
    # 类型筛选
    if item_type != 'all':
        query += " AND type = ?"
        params.append(item_type)
    
    # 状态筛选
    if status != 'all':
        query += " AND matched = ?"
        params.append(int(status))
    
    # 排序：未匹配的在前，已匹配的在后，同一状态下按时间倒序
    query += " ORDER BY matched ASC, created_at DESC"
    
    items = conn.execute(query, params).fetchall()
    conn.close()
    
    # 分类为丢失和找到的物品
    lost_items = [item for item in items if item['type'] == 'lost']
    found_items = [item for item in items if item['type'] == 'found']
    
    return render_template('index.html', lost_items=lost_items, found_items=found_items, 
                           search=True, keyword=keyword, item_type=item_type, status=status)

# 在文件底部添加
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=(os.environ.get('FLASK_DEBUG') == '1'))