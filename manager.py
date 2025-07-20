import os

from flask import render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from src import create_app

config_name = os.environ.get('FLASK_CONFIG') or 'Dev'
app = create_app(config_name)

# 配置 MySQL 数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@192.168.60.134/test_flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# 定义模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


@app.route('/')
def hello_world():
    return render_template('index.html', name="World")


@app.route('/add_user', methods=['POST'])
def add_user():
    from flask import request, jsonify

    # 从请求中获取数据
    name = request.json.get('name')
    email = request.json.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    # 创建用户实例
    new_user = User(name=name, email=email)

    try:
        # 添加到数据库会话并提交
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully',
                        'user': {'id': new_user.id, 'name': new_user.name, 'email': new_user.email}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        # 查询所有用户
        users = User.query.all()
        # 将用户数据转换为字典列表
        user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_user_by_name', methods=['GET'])
def get_user_by_name():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    try:
        # 使用参数化查询防止 SQL 注入
        sql = text('SELECT * FROM user WHERE name = :name')
        result = db.session.execute(sql, {'name': name}).fetchall()
        user_list = [{'id': row.id, 'name': row.name, 'email': row.email} for row in result]
        return jsonify(user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8081)
