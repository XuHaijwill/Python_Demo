import re
from flask import request
from flask_restful import Resource,reqparse
# pip install flask_restful==0.3.9
from flask_shop.user import user_bp,user_api
from flask_shop import models,db

from flask_shop.utils.token import generate_token,login_required
# 创建视图
@user_bp.route('/')
def index():
    return 'Hello User!!'

# 登录功能
@user_bp.route('/login/', methods=['POST'])
def login():
    # 获取用户名
    # name = request.form.get('name')  # content-type: application/x-www-form-urlencoded
    name = request.get_json().get('name')  # content-type: application/json
    # 获取密码
    pwd = request.get_json().get('pwd')
    # 判断是否传递数据完整
    if not all([name, pwd]):
        return {'status': 400, 'msg': '参数不完整'}
    else:
        # 通过用户名获取用户对象
        user = models.User.query.filter(name == name).first()
        # 判断用户是否存在
        if user:
            # 判断密码是否正确
            if user.check_password(pwd):
                # 生成一个token
                token = generate_token({'id': user.id})
                return {'status': 200, 'msg': '登录成功','data':{'token':token}}
        return {'status': 400, 'msg': '用户名或密码错误'}


class Users(Resource):
    def get(self):
        # 创建RequestParser对象
        parser = reqparse.RequestParser()
        # 添加参数
        parser.add_argument('pnum', type=int, default=1,location='args')
        parser.add_argument('psize',type=int, default=2,location='args')
        parser.add_argument('name',type=str,location='args')
        # 解析参数
        args = parser.parse_args()
        # 获取里面的数据
        name = args.get('name')
        pnum = args.get('pnum')
        psize = args.get('psize')
        # 判断是否传递了name
        if name:
            # 获取用户列表
            user_list = models.User.query.filter(models.User.name.like(f'%{name}%')).paginate(page=pnum,per_page=psize)
        else:
            # 获取用户列表
            user_list = models.User.query.paginate(page=pnum,per_page=psize)
        data= {
           'total':user_list.total,
           'pnum':pnum, 
           'data':[u.to_dict() for u in user_list.items]
        }
        return {'status':200,'msg':'获取用户列表成功','data':data}

    def post(self):
        # 注册用户
        # 接收用户信息
        name = request.get_json().get('name')
        pwd = request.get_json().get('pwd')
        real_pwd = request.get_json().get('real_pwd')
        # 验证数据的合法性
        if not all([name, pwd, real_pwd]):
            return {'status': 400, 'msg': '参数不完整'}
        # 判断两次密码是否一致
        if pwd != real_pwd:
            return {'status': 400, 'msg': '两次密码不一致'}
        # 判断用户名是否合法
        if len(name)<2:
            return {'status': 400, 'msg': '用户名不合法'}

        # 接收手机号和邮箱
        phone = request.get_json().get('phone')
        email = request.get_json().get('email')
        # 昵称
        nick_name = request.get_json().get('nick_name')
        if not re.match(r'^1[3456789]\d{9}$', phone):
            return {'status': 400, 'msg': '手机号不合法'}
        if not re.match('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            return {'status': 400, 'msg': '邮箱不合法'}
        # 接受角色ID信息
        role_id = request.get_json().get('role_id')
        try:
            # 判断用户名是否存在
            user = models.User.query.filter(models.User.name == name).first()
            if user:
                return {'status': 400, 'msg': '用户名已存在'}
        except Exception as e:
            print(e)
        # 创建用户对象
        # 判断是否传递了角色ID
        if role_id:
            user = models.User(name=name, password=pwd, phone=phone, email=email, nick_name=nick_name,role_id=role_id)
        else:
            user = models.User(name=name, password=pwd, phone=phone, email=email, nick_name=nick_name)
        # 保存到数据库
        db.session.add(user)
        db.session.commit()
        return {'status': 200, 'msg': '注册成功'}

user_api.add_resource(Users, '/users/')


class User(Resource):
    def get(self,id):
        user = models.User.query.get(id)
        if user:
            return {'status': 200, 'msg': '查询成功', 'data': user.to_dict()}
        else:
            return {'status':404,'msg':'用户不存在'}

    def put(self,id):
        try:
            user = models.User.query.get(id)
            # 创建RequestParser对象，用来接收数据
            paser = reqparse.RequestParser()
            paser.add_argument('nick_name',type=str)
            paser.add_argument('phone',type=str)
            paser.add_argument('email',type=str)
            # 增加角色ID
            paser.add_argument('role_id',type=int)
            # 解析参数
            args = paser.parse_args()
            if args.get('nick_name'):
                user.nick_name = args.get('nick_name')
            if args.get('phone'):
                user.phone = args.get('phone')
            if args.get('email'):
                user.email = args.get('email')
            # 判断是否传递了角色ID
            if args.get('role_id'):
                user.role_id = args.get('role_id')
            db.session.commit()
            return {'status':200,'msg':'修改成功','data':user.to_dict()}
        except Exception as e:
            print(e)
            return {'status':400,'msg':'修改失败'}

    def delete(self,id):
        try:
            user = models.User.query.get(id)
            if user:
                db.session.delete(user)
                db.session.commit()
            return {'status':200,'msg':'删除成功'}
        except Exception as e:
            print(e)
            return {'status':400,'msg':'删除失败'}

user_api.add_resource(User, '/user/<int:id>/')

@user_bp.route('/reset_pwd/<int:id>/')
def rest_pwd(id):
    try:
        # 根据ID获取用户信息
        user = models.User.query.get(id)
        # 重置密码
        user.password = '123456'
        # 保存到数据库
        db.session.commit()
        return {'status':200,'msg':'重置密码成功,密码为123456'}
    except Exception as e:
        print(e)
        return {'status':400,'msg':'重置密码失败'}

@user_bp.route('/test/')
@login_required
def test_login_required():
    return {'status': 200, 'msg': '验证成功'}