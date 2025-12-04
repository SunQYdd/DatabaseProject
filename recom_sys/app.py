# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
import math
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 生产环境应该使用更安全的密钥

def _env(name, default=None):
    v = os.environ.get(name)
    return v if v is not None else default

OPENGAUSS_HOST = _env('OPENGAUSS_HOST', '139.9.116.109')
OPENGAUSS_PORT = int(_env('OPENGAUSS_PORT', '26000'))
OPENGAUSS_DB = _env('OPENGAUSS_DB', 'mytest')
OPENGAUSS_USER = _env('OPENGAUSS_USER', 'sqy')
OPENGAUSS_PASSWORD = _env('OPENGAUSS_PASSWORD', '451278963Qwe')
OPENGAUSS_SSLMODE = _env('OPENGAUSS_SSLMODE')
# jdbc:postgresql://139.9.116.109:26000/mytest
DATABASE_URL = _env('DATABASE_URL', f'postgresql://{OPENGAUSS_USER}:{OPENGAUSS_PASSWORD}@{OPENGAUSS_HOST}:{OPENGAUSS_PORT}/{OPENGAUSS_DB}')
app.config['DATABASE_URL'] = DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 1800, 'pool_size': 5, 'max_overflow': 10}

DB = None

def _hash_password(p):
    s = os.environ.get('PASSWORD_SALT') or ''
    return hashlib.md5((p + s).encode('utf-8')).hexdigest()

def init_db():
    global DB
    try:
        import psycopg2
        kwargs = {
            'host': OPENGAUSS_HOST,
            'port': OPENGAUSS_PORT,
            'dbname': OPENGAUSS_DB,
            'user': OPENGAUSS_USER,
            'password': OPENGAUSS_PASSWORD
        }
        if OPENGAUSS_SSLMODE:
            kwargs['sslmode'] = OPENGAUSS_SSLMODE
        conn = psycopg2.connect(**kwargs)
        DB = {'type': 'psycopg2', 'conn': conn}
        return DB
    except Exception:
        try:
            from sqlalchemy import create_engine
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], **app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}))
            DB = {'type': 'sqlalchemy', 'engine': engine}
            return DB
        except Exception:
            DB = None
            return None

def get_db_connection():
    if DB is None:
        return None
    if DB.get('type') == 'sqlalchemy':
        return DB['engine'].connect()
    if DB.get('type') == 'psycopg2':
        conn = DB.get('conn')
        try:
            if not conn or getattr(conn, 'closed', 1) != 0:
                import psycopg2
                kwargs = {
                    'host': OPENGAUSS_HOST,
                    'port': OPENGAUSS_PORT,
                    'dbname': OPENGAUSS_DB,
                    'user': OPENGAUSS_USER,
                    'password': OPENGAUSS_PASSWORD
                }
                if OPENGAUSS_SSLMODE:
                    kwargs['sslmode'] = OPENGAUSS_SSLMODE
                DB['conn'] = psycopg2.connect(**kwargs)
                conn = DB['conn']
        except Exception:
            return None
        return conn
    return None

init_db()

# ==========================================
# 1. 模拟数据库 (In-Memory Database)
# ==========================================

# 用户表 tb_users
USERS = [
    {
        "userId": 1,
        "username": "admin",
        "password": "admin123",
        "email": "admin@example.com",
        "avatarUrl": None,
        "status": 1,
        "createdAt": datetime.now().isoformat()
    },
    {
        "userId": 2,
        "username": "user",
        "password": "password",
        "email": "user@example.com",
        "avatarUrl": None,
        "status": 1,
        "createdAt": datetime.now().isoformat()
    }
]

# 项目表 tb_items
ITEMS = [
    # Books
    {"itemId": 1, "title": "三体", "type": "book", "authorDirector": "刘慈欣", "releaseYear": 2006, "ratingAvg": 9.2, "ratingCount": 1000, "viewCount": 5000, "coverUrl": "https://luoxiadushu.com/images/2015/07/santi-1.jpg", "description": "文化大革命如火如荼进行的同时，军方探寻外星文明的绝秘计划“红岸工程”取得了突破性进展...", "createdAt": datetime.now().isoformat()},
    {"itemId": 2, "title": "活着", "type": "book", "authorDirector": "余华", "releaseYear": 1993, "ratingAvg": 9.1, "ratingCount": 900, "viewCount": 4500, "coverUrl": "https://img-s.msn.cn/tenant/amp/entityid/AA1RqLkK.img?w=600&h=590&m=6", "description": "《活着》讲述了农村人福贵悲惨的人生遭遇...", "createdAt": datetime.now().isoformat()},
    {"itemId": 3, "title": "百年孤独", "type": "book", "authorDirector": "加西亚·马尔克斯", "releaseYear": 1967, "ratingAvg": 9.2, "ratingCount": 850, "viewCount": 4000, "coverUrl": "https://img3.doubanio.com/view/subject/s/public/s27270478.jpg", "description": "《百年孤独》是魔幻现实主义文学的代表作...", "createdAt": datetime.now().isoformat()},
    {"itemId": 4, "title": "围城", "type": "book", "authorDirector": "钱钟书", "releaseYear": 1947, "ratingAvg": 8.9, "ratingCount": 800, "viewCount": 3500, "coverUrl": "https://img3.doubanio.com/view/subject/s/public/s27270479.jpg", "description": "《围城》是钱钟书所著的长篇小说...", "createdAt": datetime.now().isoformat()},
    {"itemId": 5, "title": "平凡的世界", "type": "book", "authorDirector": "路遥", "releaseYear": 1986, "ratingAvg": 9.0, "ratingCount": 950, "viewCount": 4800, "coverUrl": "https://img3.doubanio.com/view/subject/s/public/s27270480.jpg", "description": "《平凡的世界》是中国作家路遥创作的一部百万字的小说...", "createdAt": datetime.now().isoformat()},
    {"itemId": 6, "title": "红楼梦", "type": "book", "authorDirector": "曹雪芹", "releaseYear": 1791, "ratingAvg": 9.6, "ratingCount": 2000, "viewCount": 10000, "coverUrl": "https://img3.doubanio.com/view/subject/s/public/s27270481.jpg", "description": "《红楼梦》是一部具有世界影响力的人情小说...", "createdAt": datetime.now().isoformat()},
    
    # Movies (IDs start from 101 to match old data logic, though not strictly necessary)
    {"itemId": 101, "title": "肖申克的救赎", "type": "movie", "authorDirector": "弗兰克·德拉邦特", "releaseYear": 1994, "ratingAvg": 9.7, "ratingCount": 3000, "viewCount": 15000, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p480747492.jpg", "description": "一场谋杀案使银行家安迪蒙冤入狱...", "createdAt": datetime.now().isoformat()},
    {"itemId": 102, "title": "霸王别姬", "type": "movie", "authorDirector": "陈凯歌", "releaseYear": 1993, "ratingAvg": 9.6, "ratingCount": 2800, "viewCount": 14000, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p2561716440.jpg", "description": "影片讲述了一对京剧艺人半个世纪的悲欢离合...", "createdAt": datetime.now().isoformat()},
    {"itemId": 103, "title": "阿甘正传", "type": "movie", "authorDirector": "罗伯特·泽米吉斯", "releaseYear": 1994, "ratingAvg": 9.5, "ratingCount": 2500, "viewCount": 12000, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p510876377.jpg", "description": "阿甘于二战结束后不久出生...", "createdAt": datetime.now().isoformat()},
    {"itemId": 104, "title": "盗梦空间", "type": "movie", "authorDirector": "克里斯托弗·诺兰", "releaseYear": 2010, "ratingAvg": 9.3, "ratingCount": 2200, "viewCount": 11000, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p513344864.jpg", "description": "多姆·柯布是一位经验老道的窃贼...", "createdAt": datetime.now().isoformat()},
    {"itemId": 105, "title": "泰坦尼克号", "type": "movie", "authorDirector": "詹姆斯·卡梅隆", "releaseYear": 1997, "ratingAvg": 9.4, "ratingCount": 2800, "viewCount": 14000, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p457760035.jpg", "description": "1912年4月10日...", "createdAt": datetime.now().isoformat()},
    {"itemId": 106, "title": "星际穿越", "type": "movie", "authorDirector": "克里斯托弗·诺兰", "releaseYear": 2014, "ratingAvg": 9.3, "ratingCount": 2100, "viewCount": 10500, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p2206088801.jpg", "description": "在未来的地球，农作物难以生长...", "createdAt": datetime.now().isoformat()},
    {"itemId": 107, "title": "楚门的世界", "type": "movie", "authorDirector": "彼得·威尔", "releaseYear": 1998, "ratingAvg": 9.3, "ratingCount": 2300, "viewCount": 11500, "coverUrl": "https://img3.doubanio.com/view/photo/s/public/p479682983.jpg", "description": "楚门是一个平凡得不能再平凡的人...", "createdAt": datetime.now().isoformat()}
]

# 标签表 tb_tags
TAGS = [
    {"tagId": 1, "tagName": "科幻", "itemCount": 4},
    {"tagId": 2, "tagName": "剧情", "itemCount": 4},
    {"tagId": 3, "tagName": "青春", "itemCount": 3},
    {"tagId": 4, "tagName": "经典", "itemCount": 4},
    {"tagId": 5, "tagName": "爱情", "itemCount": 2},
    {"tagId": 6, "tagName": "历史", "itemCount": 2}
]

# 项目-标签关联表 tb_item_tags
ITEM_TAGS = [
    {"itemId": 1, "tagId": 1}, # 三体 - 科幻
    {"itemId": 106, "tagId": 1}, # 星际穿越 - 科幻
    {"itemId": 104, "tagId": 1}, # 盗梦空间 - 科幻
    {"itemId": 104, "tagId": 2}, # 盗梦空间 - 剧情
    {"itemId": 6, "tagId": 2}, # 红楼梦 - 剧情 (just sample logic from js)
    {"itemId": 6, "tagId": 4}, # 红楼梦 - 经典
    {"itemId": 6, "tagId": 5}, # 红楼梦 - 爱情
    {"itemId": 4, "tagId": 2}, # 围城 - 剧情
    {"itemId": 101, "tagId": 2}, # 肖申克 - 剧情
    {"itemId": 101, "tagId": 4}, # 肖申克 - 经典
    {"itemId": 107, "tagId": 2}, # 楚门 - 剧情
    {"itemId": 5, "tagId": 3}, # 平凡的世界 - 青春
    {"itemId": 5, "tagId": 6}, # 平凡的世界 - 历史
    {"itemId": 2, "tagId": 3}, # 活着 - 青春
    {"itemId": 102, "tagId": 3}, # 霸王别姬 - 青春
    {"itemId": 102, "tagId": 4}, # 霸王别姬 - 经典
    {"itemId": 3, "tagId": 4}, # 百年孤独 - 经典
    {"itemId": 105, "tagId": 5}, # 泰坦尼克 - 爱情
]

# 评分表 tb_ratings
RATINGS = []

# 收藏表 tb_favorites
FAVORITES = []

# ==========================================
# 2. 辅助函数
# ==========================================

def get_current_user():
    if 'username' not in session:
        return None
    username = session['username']
    
    # 优先尝试从数据库获取，没连上则使用内存数据
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                row = conn.execute(text("SELECT user_id, username, email, avatar_url FROM tb_users WHERE username=:u"), {"u": username}).fetchone()
                if row:
                    return {
                        "userId": row[0],
                        "username": row[1],
                        "email": row[2],
                        "avatarUrl": row[3]
                    }
            else:
                cur = conn.cursor()
                cur.execute("SELECT user_id, username, email, avatar_url FROM tb_users WHERE username=%s", (username,))
                row = cur.fetchone()
                cur.close()
                if row:
                    return {
                        "userId": row[0],
                        "username": row[1],
                        "email": row[2],
                        "avatarUrl": row[3]
                    }
        except Exception:
            pass
    
    # 数据库不可用，回退到内存用户列表
    return next((u for u in USERS if u['username'] == username), None)

def get_item_by_id(item_id):
    return next((i for i in ITEMS if i['itemId'] == item_id), None)

def get_item_tags(item_id):
    tag_ids = [it['tagId'] for it in ITEM_TAGS if it['itemId'] == item_id]
    tags = [t['tagName'] for t in TAGS if t['tagId'] in tag_ids]
    return tags

# ==========================================
# 3. 视图路由 (View Routes)
# ==========================================

@app.route('/')
def index():
    """主页"""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    """登录页面"""
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/profile')
def profile_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/detail/<item_type>/<int:item_id>')
def detail(item_type, item_id):
    if 'username' not in session:
        return redirect(url_for('login_page'))

    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                r = conn.execute(text("SELECT item_id, title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description FROM tb_items WHERE item_id=:id"), {'id': item_id}).fetchone()
                if not r:
                    conn.close()
                    return "项目未找到", 404
                item_copy = {
                    'itemId': r[0],
                    'title': r[1],
                    'type': r[2],
                    'authorDirector': r[3],
                    'releaseYear': r[4],
                    'ratingAvg': float(r[5]) if r[5] is not None else 0.0,
                    'ratingCount': int(r[6]) if r[6] is not None else 0,
                    'viewCount': int(r[7]) if r[7] is not None else 0,
                    'coverUrl': r[8],
                    'description': r[9]
                }
                trows = conn.execute(text("SELECT t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id=:id"), {'id': item_id}).fetchall()
                item_copy['tags'] = [x[0] for x in trows]
                user = get_current_user()
                item_copy['isFavorited'] = False
                item_copy['userRating'] = None
                if user:
                    fav = conn.execute(text("SELECT 1 FROM tb_favorites WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id}).fetchone()
                    item_copy['isFavorited'] = bool(fav)
                    rrow = conn.execute(text("SELECT score FROM tb_ratings WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id}).fetchone()
                    if rrow:
                        item_copy['userRating'] = int(rrow[0])
                item_copy['id'] = item_copy['itemId']
                item_copy['year'] = item_copy['releaseYear']
                item_copy['rating'] = item_copy['ratingAvg']
                item_copy['cover'] = item_copy['coverUrl']
                if item_copy['type'] == 'book':
                    item_copy['author'] = item_copy['authorDirector']
                else:
                    item_copy['director'] = item_copy['authorDirector']
                conn.close()
                return render_template('detail.html', item=item_copy, item_type=item_type)
            else:
                cur = conn.cursor()
                cur.execute("SELECT item_id, title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description FROM tb_items WHERE item_id=%s", (item_id,))
                r = cur.fetchone()
                if not r:
                    cur.close()
                    return "项目未找到", 404
                item_copy = {
                    'itemId': r[0], 'title': r[1], 'type': r[2], 'authorDirector': r[3], 'releaseYear': r[4], 'ratingAvg': float(r[5]) if r[5] is not None else 0.0, 'ratingCount': int(r[6]) if r[6] is not None else 0, 'viewCount': int(r[7]) if r[7] is not None else 0, 'coverUrl': r[8], 'description': r[9]
                }
                cur.execute("SELECT t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id=%s", (item_id,))
                item_copy['tags'] = [x[0] for x in cur.fetchall()]
                user = get_current_user()
                item_copy['isFavorited'] = False
                item_copy['userRating'] = None
                if user:
                    cur.execute("SELECT 1 FROM tb_favorites WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                    item_copy['isFavorited'] = cur.fetchone() is not None
                    cur.execute("SELECT score FROM tb_ratings WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                    rrow = cur.fetchone()
                    if rrow:
                        item_copy['userRating'] = int(rrow[0])
                cur.close()
                item_copy['id'] = item_copy['itemId']
                item_copy['year'] = item_copy['releaseYear']
                item_copy['rating'] = item_copy['ratingAvg']
                item_copy['cover'] = item_copy['coverUrl']
                if item_copy['type'] == 'book':
                    item_copy['author'] = item_copy['authorDirector']
                else:
                    item_copy['director'] = item_copy['authorDirector']
                return render_template('detail.html', item=item_copy, item_type=item_type)
        except Exception:
            pass

    return "数据库不可用", 500

# ==========================================
# 4. API 接口 (API Routes)
# ==========================================

# --- 4.1 公共接口 (/api/public) ---

@app.route('/api/public/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    now_dt = datetime.now()
    new_id = None
    hashed = _hash_password(password or '')
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                with conn.begin():
                    exists = conn.execute(text("SELECT 1 FROM tb_users WHERE username=:username"), {"username": username}).fetchone()
                    if exists:
                        return jsonify({"code": 400, "message": "用户名已存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                    row = conn.execute(text("INSERT INTO tb_users (username, password, email, avatar_url, status, created_at) VALUES (:username, :password, :email, :avatar_url, :status, :created_at) RETURNING user_id"), {"username": username, "password": hashed, "email": email, "avatar_url": None, "status": 1, "created_at": now_dt}).fetchone()
                    if row:
                        new_id = row[0]
                conn.close()
            else:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM tb_users WHERE username=%s", (username,))
                if cur.fetchone():
                    cur.close()
                    return jsonify({"code": 400, "message": "用户名已存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                cur.execute("INSERT INTO tb_users (username, password, email, avatar_url, status, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id", (username, hashed, email, None, 1, now_dt))
                row = cur.fetchone()
                if row:
                    new_id = row[0]
                conn.commit()
                cur.close()
        except Exception:
            try:
                if DB.get('type') == 'sqlalchemy':
                    from sqlalchemy import text
                    conn.execute(text("CREATE TABLE IF NOT EXISTS tb_users (user_id BIGSERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, email VARCHAR(100), avatar_url VARCHAR(255), status SMALLINT NOT NULL DEFAULT 1, created_at TIMESTAMP NOT NULL)"))
                    row = conn.execute(text("INSERT INTO tb_users (username, password, email, avatar_url, status, created_at) VALUES (:username, :password, :email, :avatar_url, :status, :created_at) RETURNING user_id"), {"username": username, "password": hashed, "email": email, "avatar_url": None, "status": 1, "created_at": now_dt}).fetchone()
                    if row:
                        new_id = row[0]
                    conn.close()
                else:
                    cur = conn.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS tb_users (user_id BIGSERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, email VARCHAR(100), avatar_url VARCHAR(255), status SMALLINT NOT NULL DEFAULT 1, created_at TIMESTAMP NOT NULL)")
                    cur.execute("INSERT INTO tb_users (username, password, email, avatar_url, status, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id", (username, hashed, email, None, 1, now_dt))
                    row = cur.fetchone()
                    if row:
                        new_id = row[0]
                    conn.commit()
                    cur.close()
            except Exception:
                new_id = None
    if new_id is None:
        if any(u['username'] == username for u in USERS):
            return jsonify({"code": 400, "message": "用户名已存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
        new_user = {
            "userId": len(USERS) + 1,
            "username": username,
            "password": hashed,
            "email": email,
            "avatarUrl": None,
            "status": 1,
            "createdAt": now_dt.isoformat()
        }
        USERS.append(new_user)
        return jsonify({
            "code": 200,
            "message": "注册成功",
            "data": {"userId": new_user['userId'], "username": new_user['username']},
            "timestamp": int(datetime.now().timestamp() * 1000)
        })
    USERS.append({
        "userId": new_id,
        "username": username,
        "password": hashed,
        "email": email,
        "avatarUrl": None,
        "status": 1,
        "createdAt": now_dt.isoformat()
    })
    return jsonify({
        "code": 200,
        "message": "注册成功",
        "data": {"userId": new_id, "username": username},
        "timestamp": int(datetime.now().timestamp() * 1000)
    })

@app.route('/api/public/login', methods=['POST'])
def api_public_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            "code": 400,
            "message": "缺少用户名或密码",
            "data": None,
            "timestamp": int(datetime.now().timestamp() * 1000)
        })

    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                exists_row = conn.execute(text("SELECT user_id, password FROM tb_users WHERE username=:u"), {"u": username}).fetchone()
                if not exists_row:
                    conn.close()
                    return jsonify({"code": 401, "message": "用户名不存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                if exists_row[1] != _hash_password(password):
                    conn.close()
                    return jsonify({"code": 401, "message": "用户名或密码错误", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                session['username'] = username
                resp = jsonify({
                    "code": 200,
                    "message": "登录成功",
                    "data": {
                        "accessToken": "mock_token",
                        "user": {"userId": exists_row[0], "username": username}
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                })
                conn.close()
                return resp
            else:
                cur = conn.cursor()
                cur.execute("SELECT user_id, password FROM tb_users WHERE username=%s", (username,))
                exists_row = cur.fetchone()
                cur.close()
                if not exists_row:
                    return jsonify({"code": 401, "message": "用户名不存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                if exists_row[1] != _hash_password(password):
                    return jsonify({"code": 401, "message": "用户名或密码错误", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
                session['username'] = username
                return jsonify({
                    "code": 200,
                    "message": "登录成功",
                    "data": {
                        "accessToken": "mock_token",
                        "user": {"userId": exists_row[0], "username": username}
                    },
                    "timestamp": int(datetime.now().timestamp() * 1000)
                })
        except Exception:
            pass

    user = next((u for u in USERS if u['username'] == username and u['password'] == password), None)
    if user:
        session['username'] = username
        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "accessToken": "mock_token",
                "user": {"userId": user['userId'], "username": user['username']}
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        })
    if not any(u['username'] == username for u in USERS):
        return jsonify({"code": 401, "message": "用户名不存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
    return jsonify({"code": 401, "message": "用户名或密码错误", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})

# 兼容旧接口 /api/login
@app.route('/api/login', methods=['POST'])
def api_login_compat():
    return api_public_login()

@app.route('/api/public/items', methods=['GET'])
def api_get_items():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 100))
    item_type = request.args.get('type')
    keyword = request.args.get('keyword', '').lower()
    tag_id = request.args.get('tagId')
    sort_by = request.args.get('sortBy', 'createdAt')
    order = request.args.get('order', 'desc').lower()
    if order not in ('asc','desc'):
        order = 'desc'

    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                params = {}
                where = []
                if item_type:
                    if item_type == 'books':
                        where.append("i.type='book'")
                    elif item_type == 'movies':
                        where.append("i.type='movie'")
                    else:
                        where.append("i.type=:type")
                        params['type'] = item_type
                if keyword:
                    where.append("(LOWER(i.title) LIKE :kw OR LOWER(i.author_director) LIKE :kw)")
                    params['kw'] = f"%{keyword}%"
                join = ''
                if tag_id:
                    join = 'JOIN tb_item_tags it ON it.item_id=i.item_id AND it.tag_id=:tagId'
                    params['tagId'] = int(tag_id)
                where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''
                count_sql = f"SELECT COUNT(*) FROM tb_items i {join} {where_sql}"
                total = conn.execute(text(count_sql), params).scalar() or 0
                offset = (page - 1) * size
                col_map = {'createdAt': 'i.created_at', 'ratingAvg': 'i.rating_avg', 'viewCount': 'i.view_count'}
                sort_col = col_map.get(sort_by, 'i.created_at')
                list_sql = f"SELECT i.item_id, i.title, i.type, i.author_director, i.release_year, i.rating_avg, i.rating_count, i.view_count, i.cover_url, i.description FROM tb_items i {join} {where_sql} ORDER BY {sort_col} {order.upper()} LIMIT :size OFFSET :offset"
                params['size'] = size
                params['offset'] = offset
                rows = conn.execute(text(list_sql), params).fetchall()
                records = []
                for r in rows:
                    d = {
                        'itemId': r[0],
                        'title': r[1],
                        'type': r[2],
                        'authorDirector': r[3],
                        'releaseYear': r[4],
                        'ratingAvg': float(r[5]) if r[5] is not None else 0.0,
                        'ratingCount': int(r[6]) if r[6] is not None else 0,
                        'viewCount': int(r[7]) if r[7] is not None else 0,
                        'coverUrl': r[8],
                        'description': r[9]
                    }
                    records.append(d)
                if records:
                    for rec in records:
                        trows = conn.execute(text("SELECT t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id=:iid"), {'iid': rec['itemId']}).fetchall()
                        rec['tags'] = [x[0] for x in trows]
                return jsonify({
                    'code': 200,
                    'message': 'success',
                    'data': {
                        'currentPage': page,
                        'pageSize': size,
                        'total': int(total),
                        'totalPages': math.ceil(total / size) if size else 0,
                        'records': records,
                        'hasPrevious': page > 1,
                        'hasNext': (offset + size) < total
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                })
            else:
                cur = conn.cursor()
                params = []
                where = []
                if item_type:
                    if item_type == 'books':
                        where.append("i.type='book'")
                    elif item_type == 'movies':
                        where.append("i.type='movie'")
                    else:
                        where.append("i.type=%s")
                        params.append(item_type)
                if keyword:
                    where.append("(LOWER(i.title) LIKE %s OR LOWER(i.author_director) LIKE %s)")
                    params.extend([f"%{keyword}%", f"%{keyword}%"])
                join = ''
                if tag_id:
                    join = 'JOIN tb_item_tags it ON it.item_id=i.item_id AND it.tag_id=%s'
                    params.append(int(tag_id))
                where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''
                cur.execute(f"SELECT COUNT(*) FROM tb_items i {join} {where_sql}", params)
                total = cur.fetchone()[0]
                offset = (page - 1) * size
                col_map = {'createdAt': 'i.created_at', 'ratingAvg': 'i.rating_avg', 'viewCount': 'i.view_count'}
                sort_col = col_map.get(sort_by, 'i.created_at')
                cur.execute(f"SELECT i.item_id, i.title, i.type, i.author_director, i.release_year, i.rating_avg, i.rating_count, i.view_count, i.cover_url, i.description FROM tb_items i {join} {where_sql} ORDER BY {sort_col} {order.upper()} LIMIT %s OFFSET %s", params + [size, offset])
                rows = cur.fetchall()
                records = []
                for r in rows:
                    records.append({
                        'itemId': r[0],
                        'title': r[1],
                        'type': r[2],
                        'authorDirector': r[3],
                        'releaseYear': r[4],
                        'ratingAvg': float(r[5]) if r[5] is not None else 0.0,
                        'ratingCount': int(r[6]) if r[6] is not None else 0,
                        'viewCount': int(r[7]) if r[7] is not None else 0,
                        'coverUrl': r[8],
                        'description': r[9]
                    })
                if records:
                    ids = tuple(rec['itemId'] for rec in records)
                    cur.execute("SELECT it.item_id, t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id IN %s", (ids,))
                    tag_rows = cur.fetchall()
                    tag_map = {}
                    for ir in tag_rows:
                        tag_map.setdefault(ir[0], []).append(ir[1])
                    for rec in records:
                        rec['tags'] = tag_map.get(rec['itemId'], [])
                cur.close()
                return jsonify({
                    'code': 200,
                    'message': 'success',
                    'data': {
                        'currentPage': page,
                        'pageSize': size,
                        'total': int(total),
                        'totalPages': math.ceil(total / size) if size else 0,
                        'records': records,
                        'hasPrevious': page > 1,
                        'hasNext': (offset + size) < total
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                })
        except Exception:
            pass
    # 数据库不可用时，或者图书/电影目录需要使用内存数据，直接返回（数据库不可用）
    if item_type in ('book','books','movie','movies'):
        return jsonify({
            'code': 500,
            'message': '数据库不可用',
            'data': {
                'currentPage': page,
                'pageSize': size,
                'total': 0,
                'totalPages': 0,
                'records': [],
                'hasPrevious': False,
                'hasNext': False
            },
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 500
    if tag_id:
        return jsonify({
            'code': 500,
            'message': '数据库不可用',
            'data': {
                'currentPage': page,
                'pageSize': size,
                'total': 0,
                'totalPages': 0,
                'records': [],
                'hasPrevious': False,
                'hasNext': False
            },
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 500

    filtered_items = ITEMS
    if item_type:
        if item_type == 'books':
            filtered_items = [i for i in filtered_items if i['type'] == 'book']
        elif item_type == 'movies':
            filtered_items = [i for i in filtered_items if i['type'] == 'movie']
        else:
            filtered_items = [i for i in filtered_items if i['type'] == item_type]
    if keyword:
        filtered_items = [i for i in filtered_items if keyword in i['title'].lower() or keyword in i['authorDirector'].lower()]
    if tag_id:
        tag_id = int(tag_id)
        item_ids_with_tag = [it['itemId'] for it in ITEM_TAGS if it['tagId'] == tag_id]
        filtered_items = [i for i in filtered_items if i['itemId'] in item_ids_with_tag]
    col_map_mem = {'createdAt': 'createdAt', 'ratingAvg': 'ratingAvg', 'viewCount': 'viewCount'}
    sort_key = col_map_mem.get(sort_by, 'createdAt')
    try:
        if sort_key == 'createdAt':
            filtered_items = sorted(filtered_items, key=lambda i: i.get('createdAt') or '', reverse=(order=='desc'))
        else:
            filtered_items = sorted(filtered_items, key=lambda i: i.get(sort_key) or 0, reverse=(order=='desc'))
    except Exception:
        pass
    total = len(filtered_items)
    start = (page - 1) * size
    end = start + size
    records = filtered_items[start:end]
    for record in records:
        record['tags'] = get_item_tags(record['itemId'])
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'currentPage': page,
            'pageSize': size,
            'total': total,
            'totalPages': math.ceil(total / size),
            'records': records,
            'hasPrevious': page > 1,
            'hasNext': end < total
        },
        'timestamp': int(datetime.now().timestamp() * 1000)
    })

@app.route('/api/public/items/<int:item_id>', methods=['GET'])
def api_get_item_detail(item_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                r = conn.execute(text("SELECT item_id, title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description FROM tb_items WHERE item_id=:id"), {'id': item_id}).fetchone()
                if not r:
                    return jsonify({'code': 404, 'message': '资源未找到', 'data': None}), 404
                item_res = {
                    'itemId': r[0],
                    'title': r[1],
                    'type': r[2],
                    'authorDirector': r[3],
                    'releaseYear': r[4],
                    'ratingAvg': float(r[5]) if r[5] is not None else 0.0,
                    'ratingCount': int(r[6]) if r[6] is not None else 0,
                    'viewCount': int(r[7]) if r[7] is not None else 0,
                    'coverUrl': r[8],
                    'description': r[9]
                }
                trows = conn.execute(text("SELECT t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id=:id"), {'id': item_id}).fetchall()
                item_res['tags'] = [x[0] for x in trows]
                user = get_current_user()
                item_res['isFavorited'] = False
                item_res['userRating'] = None
                if user:
                    fav = conn.execute(text("SELECT 1 FROM tb_favorites WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id}).fetchone()
                    item_res['isFavorited'] = bool(fav)
                    rrow = conn.execute(text("SELECT score FROM tb_ratings WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id}).fetchone()
                    if rrow:
                        item_res['userRating'] = int(rrow[0])
                return jsonify({'code': 200, 'message': 'success', 'data': item_res, 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("SELECT item_id, title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description FROM tb_items WHERE item_id=%s", (item_id,))
                r = cur.fetchone()
                if not r:
                    cur.close()
                    return jsonify({'code': 404, 'message': '资源未找到', 'data': None}), 404
                item_res = {
                    'itemId': r[0], 'title': r[1], 'type': r[2], 'authorDirector': r[3], 'releaseYear': r[4], 'ratingAvg': float(r[5]) if r[5] is not None else 0.0, 'ratingCount': int(r[6]) if r[6] is not None else 0, 'viewCount': int(r[7]) if r[7] is not None else 0, 'coverUrl': r[8], 'description': r[9]
                }
                cur.execute("SELECT t.tag_name FROM tb_item_tags it JOIN tb_tags t ON t.tag_id=it.tag_id WHERE it.item_id=%s", (item_id,))
                item_res['tags'] = [x[0] for x in cur.fetchall()]
                user = get_current_user()
                item_res['isFavorited'] = False
                item_res['userRating'] = None
                if user:
                    cur.execute("SELECT 1 FROM tb_favorites WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                    item_res['isFavorited'] = cur.fetchone() is not None
                    cur.execute("SELECT score FROM tb_ratings WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                    rrow = cur.fetchone()
                    if rrow:
                        item_res['userRating'] = int(rrow[0])
                cur.close()
                return jsonify({'code': 200, 'message': 'success', 'data': item_res, 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception:
            pass
    return jsonify({'code': 500, 'message': '数据库不可用', 'data': None, 'timestamp': int(datetime.now().timestamp() * 1000)}), 500

@app.route('/api/public/tags', methods=['GET'])
def api_get_tags():
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                rows = conn.execute(text("SELECT tag_id, tag_name, COALESCE(item_count,0) FROM tb_tags ORDER BY tag_id")).fetchall()
                records = [{'tagId': r[0], 'tagName': r[1], 'itemCount': int(r[2])} for r in rows]
                return jsonify({'code': 200, 'message': 'success', 'data': {'records': records}, 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("SELECT tag_id, tag_name, COALESCE(item_count,0) FROM tb_tags ORDER BY tag_id")
                rows = cur.fetchall()
                cur.close()
                records = [{'tagId': r[0], 'tagName': r[1], 'itemCount': int(r[2])} for r in rows]
                return jsonify({'code': 200, 'message': 'success', 'data': {'records': records}, 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception:
            pass
    return jsonify({'code': 200, 'message': 'success', 'data': {'records': TAGS}, 'timestamp': int(datetime.now().timestamp() * 1000)})

# --- 4.2 用户接口 (/api/user) ---

@app.route('/api/user/profile', methods=['GET','PUT'])
def api_user_profile():
    user = get_current_user()
    if not user:
        return jsonify({"code": 401, "message": "未授权", "data": None}), 401
    if request.method == 'GET':
        return jsonify({
            "code": 200,
            "message": "success",
            "data": {
                "userId": user['userId'],
                "username": user['username'],
                "email": user['email'],
                "avatarUrl": user['avatarUrl']
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        })
    data = request.get_json() or {}
    new_username = data.get('username')
    new_email = data.get('email')
    new_avatar = data.get('avatarUrl')
    old_password = data.get('oldPassword')
    new_password = data.get('password')
    if new_password is not None:
        if user['password'] != (old_password or ''):
            return jsonify({"code": 400, "message": "旧密码不正确", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
        user['password'] = new_password
    if new_username is not None:
        if any(u['username'] == new_username and u['userId'] != user['userId'] for u in USERS):
            return jsonify({"code": 400, "message": "用户名已存在", "data": None, "timestamp": int(datetime.now().timestamp() * 1000)})
        session['username'] = new_username
        user['username'] = new_username
    if new_email is not None:
        user['email'] = new_email
    if new_avatar is not None:
        user['avatarUrl'] = new_avatar
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "userId": user['userId'],
            "username": user['username'],
            "email": user['email'],
            "avatarUrl": user['avatarUrl']
        },
        "timestamp": int(datetime.now().timestamp() * 1000)
    })

@app.route('/api/user/items/<int:item_id>/rate', methods=['POST'])
def api_rate_item(item_id):
    user = get_current_user()
    if not user:
        return jsonify({'code': 401, 'message': '未授权'}), 401
    data = request.get_json()
    score = data.get('score')
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                with conn.begin():
                    conn.execute(text("DELETE FROM tb_ratings WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id})
                    conn.execute(text("INSERT INTO tb_ratings (user_id, item_id, score, created_at) VALUES (:uid, :iid, :score, :ts)"), {'uid': user['userId'], 'iid': item_id, 'score': int(score), 'ts': datetime.now()})
                    agg = conn.execute(text("SELECT AVG(score), COUNT(*) FROM tb_ratings WHERE item_id=:iid"), {'iid': item_id}).fetchone()
                    avg = float(agg[0]) if agg and agg[0] is not None else 0.0
                    cnt = int(agg[1]) if agg and agg[1] is not None else 0
                    conn.execute(text("UPDATE tb_items SET rating_avg=:avg, rating_count=:cnt WHERE item_id=:iid"), {'avg': avg, 'cnt': cnt, 'iid': item_id})
                return jsonify({'code': 200, 'message': '评分成功', 'data': {'ratingAvg': avg, 'ratingCount': cnt}, 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("DELETE FROM tb_ratings WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                cur.execute("INSERT INTO tb_ratings (user_id, item_id, score, created_at) VALUES (%s, %s, %s, %s)", (user['userId'], item_id, int(score), datetime.now()))
                cur.execute("SELECT AVG(score), COUNT(*) FROM tb_ratings WHERE item_id=%s", (item_id,))
                agg = cur.fetchone()
                avg = float(agg[0]) if agg and agg[0] is not None else 0.0
                cnt = int(agg[1]) if agg and agg[1] is not None else 0
                cur.execute("UPDATE tb_items SET rating_avg=%s, rating_count=%s WHERE item_id=%s", (avg, cnt, item_id))
                conn.commit()
                cur.close()
                return jsonify({'code': 200, 'message': '评分成功', 'data': {'ratingAvg': avg, 'ratingCount': cnt}, 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception:
            pass
    global RATINGS
    RATINGS = [r for r in RATINGS if not (r['userId'] == user['userId'] and r['itemId'] == item_id)]
    RATINGS.append({'ratingId': len(RATINGS) + 1, 'userId': user['userId'], 'itemId': item_id, 'score': score, 'createdAt': datetime.now().isoformat()})
    item = get_item_by_id(item_id)
    item_ratings = [r['score'] for r in RATINGS if r['itemId'] == item_id]
    item['ratingCount'] = len(item_ratings)
    item['ratingAvg'] = round(sum(item_ratings) / len(item_ratings), 2)
    return jsonify({'code': 200, 'message': '评分成功', 'data': {'ratingAvg': item['ratingAvg'], 'ratingCount': item['ratingCount']}, 'timestamp': int(datetime.now().timestamp() * 1000)})

@app.route('/api/user/items/<int:item_id>/favorite', methods=['POST'])
def api_favorite_item(item_id):
    user = get_current_user()
    if not user:
        return jsonify({'code': 401, 'message': '未授权'}), 401
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                with conn.begin():
                    ex = conn.execute(text("SELECT 1 FROM tb_favorites WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id}).fetchone()
                    if ex:
                        conn.execute(text("DELETE FROM tb_favorites WHERE user_id=:uid AND item_id=:iid"), {'uid': user['userId'], 'iid': item_id})
                        return jsonify({'code': 200, 'message': '收藏成功', 'data': {'isFavorited': False}, 'timestamp': int(datetime.now().timestamp() * 1000)})
                    else:
                        conn.execute(text("INSERT INTO tb_favorites (user_id, item_id, created_at) VALUES (:uid, :iid, :ts)"), {'uid': user['userId'], 'iid': item_id, 'ts': datetime.now()})
                        return jsonify({'code': 200, 'message': '收藏成功', 'data': {'isFavorited': True}, 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM tb_favorites WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                ex = cur.fetchone()
                if ex:
                    cur.execute("DELETE FROM tb_favorites WHERE user_id=%s AND item_id=%s", (user['userId'], item_id))
                    conn.commit()
                    cur.close()
                    return jsonify({'code': 200, 'message': '收藏成功', 'data': {'isFavorited': False}, 'timestamp': int(datetime.now().timestamp() * 1000)})
                cur.execute("INSERT INTO tb_favorites (user_id, item_id, created_at) VALUES (%s, %s, %s)", (user['userId'], item_id, datetime.now()))
                conn.commit()
                cur.close()
                return jsonify({'code': 200, 'message': '收藏成功', 'data': {'isFavorited': True}, 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception:
            pass
    global FAVORITES
    existing = next((f for f in FAVORITES if f['userId'] == user['userId'] and f['itemId'] == item_id), None)
    is_favorited = False
    if existing:
        FAVORITES.remove(existing)
        is_favorited = False
    else:
        FAVORITES.append({'favoriteId': len(FAVORITES) + 1, 'userId': user['userId'], 'itemId': item_id, 'createdAt': datetime.now().isoformat()})
        is_favorited = True
    return jsonify({'code': 200, 'message': '收藏成功', 'data': {'isFavorited': is_favorited}, 'timestamp': int(datetime.now().timestamp() * 1000)})

@app.route('/api/user/favorites', methods=['GET'])
def api_get_favorites():
    user = get_current_user()
    if not user:
        return jsonify({'code': 401, 'message': '未授权'}), 401
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                rows = conn.execute(text("SELECT i.item_id, i.title, i.type, i.author_director, i.release_year, i.rating_avg, i.rating_count, i.view_count, i.cover_url, i.description FROM tb_items i JOIN tb_favorites f ON f.item_id=i.item_id WHERE f.user_id=:uid ORDER BY f.created_at DESC"), {'uid': user['userId']}).fetchall()
                items = []
                for r in rows:
                    items.append({'itemId': r[0], 'title': r[1], 'type': r[2], 'authorDirector': r[3], 'releaseYear': r[4], 'ratingAvg': float(r[5]) if r[5] is not None else 0.0, 'ratingCount': int(r[6]) if r[6] is not None else 0, 'viewCount': int(r[7]) if r[7] is not None else 0, 'coverUrl': r[8], 'description': r[9]})
                return jsonify({'code': 200, 'message': 'success', 'data': {'records': items}, 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("SELECT i.item_id, i.title, i.type, i.author_director, i.release_year, i.rating_avg, i.rating_count, i.view_count, i.cover_url, i.description FROM tb_items i JOIN tb_favorites f ON f.item_id=i.item_id WHERE f.user_id=%s ORDER BY f.created_at DESC", (user['userId'],))
                rows = cur.fetchall()
                cur.close()
                items = [{'itemId': r[0], 'title': r[1], 'type': r[2], 'authorDirector': r[3], 'releaseYear': r[4], 'ratingAvg': float(r[5]) if r[5] is not None else 0.0, 'ratingCount': int(r[6]) if r[6] is not None else 0, 'viewCount': int(r[7]) if r[7] is not None else 0, 'coverUrl': r[8], 'description': r[9]} for r in rows]
                return jsonify({'code': 200, 'message': 'success', 'data': {'records': items}, 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception:
            pass
    fav_item_ids = [f['itemId'] for f in FAVORITES if f['userId'] == user['userId']]
    items = [i for i in ITEMS if i['itemId'] in fav_item_ids]
    return jsonify({'code': 200, 'message': 'success', 'data': {'records': items}, 'timestamp': int(datetime.now().timestamp() * 1000)})

@app.route('/api/user/recommendations/tag-based', methods=['GET'])
def api_tag_recommendations():
    # 简单模拟：返回前5个
    user = get_current_user()
    if not user:
         return jsonify({"code": 401, "message": "未授权"}), 401
         
    recs = ITEMS[:5] # 简单返回前5个
    for rec in recs:
        rec['tags'] = get_item_tags(rec['itemId'])
        
    return jsonify({
        "code": 200,
        "message": "success",
        "data": recs,
        "timestamp": int(datetime.now().timestamp() * 1000)
    })

# --- 4.3 数据接口 ---

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({"success": True, "message": "已登出"})

# 兼容前端的添加接口
@app.route('/api/items', methods=['POST'])
def api_add_item():
    if 'username' not in session:
        return jsonify({'success': False, 'message': '未授权'}), 401
    data = request.get_json()
    item_data = data.get('item')
    type_str = data.get('type')
    conn = get_db_connection()
    if conn is not None:
        try:
            content_type = 'book' if type_str == 'books' else 'movie'
            author_director = item_data.get('author') if type_str == 'books' else item_data.get('director')
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                with conn.begin():
                    row = conn.execute(text("INSERT INTO tb_items (title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description, created_at) VALUES (:title, :type, :ad, :year, :rating, 0, 0, :cover, :desc, :ts) RETURNING item_id"), {
                        'title': item_data.get('title'),
                        'type': content_type,
                        'ad': author_director,
                        'year': int(item_data.get('year')),
                        'rating': float(item_data.get('rating')),
                        'cover': item_data.get('cover'),
                        'desc': item_data.get('description'),
                        'ts': datetime.now()
                    }).fetchone()
                resp = jsonify({'success': True, 'message': '添加成功', 'data': {'itemId': row[0]}})
                conn.close()
                return resp
            else:
                cur = conn.cursor()
                cur.execute("INSERT INTO tb_items (title, type, author_director, release_year, rating_avg, rating_count, view_count, cover_url, description, created_at) VALUES (%s, %s, %s, %s, %s, 0, 0, %s, %s, %s) RETURNING item_id", (item_data.get('title'), content_type, author_director, int(item_data.get('year')), float(item_data.get('rating')), item_data.get('cover'), item_data.get('description'), datetime.now()))
                row = cur.fetchone()
                conn.commit()
                cur.close()
                return jsonify({'success': True, 'message': '添加成功', 'data': {'itemId': row[0]}})
        except Exception:
            pass
    new_id = max([i['itemId'] for i in ITEMS] or [0]) + 1
    new_item = {'itemId': new_id, 'title': item_data.get('title'), 'type': 'book' if type_str == 'books' else 'movie', 'authorDirector': item_data.get('author') if type_str == 'books' else item_data.get('director'), 'releaseYear': item_data.get('year'), 'ratingAvg': item_data.get('rating'), 'ratingCount': 0, 'viewCount': 0, 'coverUrl': item_data.get('cover'), 'description': item_data.get('description'), 'createdAt': datetime.now().isoformat()}
    ITEMS.append(new_item)
    return jsonify({'success': True, 'message': '添加成功'})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    if 'username' not in session:
        return jsonify({'code': 401, 'message': '未授权'}), 401
    
    conn = get_db_connection()
    if conn is not None:
        try:
            if DB.get('type') == 'sqlalchemy':
                from sqlalchemy import text
                with conn.begin():
                    conn.execute(text("DELETE FROM tb_item_tags WHERE item_id=:id"), {'id': item_id})
                    conn.execute(text("DELETE FROM tb_ratings WHERE item_id=:id"), {'id': item_id})
                    conn.execute(text("DELETE FROM tb_favorites WHERE item_id=:id"), {'id': item_id})
                    result = conn.execute(text("DELETE FROM tb_items WHERE item_id=:id"), {'id': item_id})
                
                if result.rowcount == 0:
                     return jsonify({'code': 404, 'message': '项目不存在', 'timestamp': int(datetime.now().timestamp() * 1000)})
                
                return jsonify({'code': 200, 'message': '删除成功', 'timestamp': int(datetime.now().timestamp() * 1000)})
            else:
                cur = conn.cursor()
                cur.execute("DELETE FROM tb_item_tags WHERE item_id=%s", (item_id,))
                cur.execute("DELETE FROM tb_ratings WHERE item_id=%s", (item_id,))
                cur.execute("DELETE FROM tb_favorites WHERE item_id=%s", (item_id,))
                cur.execute("DELETE FROM tb_items WHERE item_id=%s", (item_id,))
                
                deleted_count = cur.rowcount
                conn.commit()
                cur.close()
                
                if deleted_count == 0:
                     return jsonify({'code': 404, 'message': '项目不存在', 'timestamp': int(datetime.now().timestamp() * 1000)})

                return jsonify({'code': 200, 'message': '删除成功', 'timestamp': int(datetime.now().timestamp() * 1000)})
        except Exception as e:
            print(f"Delete error: {e}")
            return jsonify({'code': 500, 'message': '数据库操作失败', 'timestamp': int(datetime.now().timestamp() * 1000)}), 500

    global ITEMS
    initial_len = len(ITEMS)
    ITEMS = [i for i in ITEMS if i['itemId'] != item_id]
    if len(ITEMS) < initial_len:
         return jsonify({'code': 200, 'message': '删除成功 (内存)', 'timestamp': int(datetime.now().timestamp() * 1000)})
         
    return jsonify({'code': 404, 'message': '项目不存在', 'timestamp': int(datetime.now().timestamp() * 1000)})

@app.route('/api/recommendations/<item_type>')
def api_recommendations_compat(item_type):
    """兼容旧的 script.js 调用，直接 js 模拟调用"""
    # 实际接口实现会被 script.js 调用，这里模拟返回
    return api_get_items()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
