from flask_restful import Resource,reqparse
from flask import request
from flask_shop import db

from flask_shop import models
from flask_shop.role import role_api,role_bp

class Roles(Resource):
    def get(self):
        '''
        获取角色列表
        '''
        try:
            roles = models.Role.query.all()
            role_list = [role.to_dict() for role in roles]
            return {'status': 200, 'msg': '获取角色列表成功', 'data': role_list}
        except Exception as e:
            return {'status': 500, 'msg': '获取角色列表失败'}
    def post(self):
        '''
        添加角色
        '''
        try:
            # 获取传递的名称
            name = request.get_json().get('name') # appliction/json
            # 获取传递的描述
            desc = request.get_json().get('desc')
            role = models.Role(name=name, desc=desc)
            # 添加到数据库会话
            db.session.add(role) 
            # 提交到数据库 
            db.session.commit()
            return {'status': 200, 'msg': '添加角色成功'}
        except Exception as e:
            return {'status': 500, 'msg': '添加角色失败'}

role_api.add_resource(Roles, '/roles/')

class Role(Resource):
    def delete(self, id):
        '''
        删除角色
        '''
        try:
            role = models.Role.query.get(id)
            db.session.delete(role)
            db.session.commit()
            return {'status': 200, 'msg': '删除角色成功'}
        except Exception as e:
            return {'status': 500, 'msg': '删除角色失败'}
    def put(self,id):
        '''
        修改角色
        '''
        try:
            role = models.Role.query.get(id)
            # 创建RequestParser对象,用来接收数据
            parser = reqparse.RequestParser()
            # 添加参数
            parser.add_argument('name', type=str, required=True, help='请输入角色名称')
            parser.add_argument('desc', type=str)
            # 解析参数
            args = parser.parse_args()
            if args.get('name'):
                role.name = args.name
            if args.get('desc'):
                role.desc = args.desc
            db.session.commit()
            return {'status': 200, 'msg': '修改角色成功'}
        except Exception as e:
            print(e)
            return {'status': 500, 'msg': '修改角色失败'}

role_api.add_resource(Role, '/role/<int:id>/')

@role_bp.route('/role/<int:rid>/<int:mid>/')
def del_menu(rid:int,mid:int):
    # 查找当前的角色信息
    role = models.Role.query.get(rid)
    # 查找当前的菜单信息
    menu = models.Menu.query.get(mid)
    # 判断当前角色与菜单是否存在
    if all([role,menu]):
        # 判断当前角色是否有当前菜单
        if menu in role.menus:
            # 删除当前角色的当前菜单
            role.menus.remove(menu)
            # 判断当前菜单是否是父菜单
            if menu.level == 1:
                # 删除当前角色，父菜单的所有子菜单
                for temp in menu.children:
                    # 判断当前角色是否有当前子菜单
                    if temp in role.menus:
                        # 删除当前角色的当前子菜单
                        role.menus.remove(temp)
        # 提交到数据库
        db.session.commit()
        return {'status': 200,'msg': '删除角色菜单成功'}
    else:
        return {'status': 500, 'msg': '角色或菜单不存在'}
    
@role_bp.route('/role/<int:rid>/',methods=['POST'])
def set_menu(rid:int):
    try:
        # 获取当前角色信息
        role = models.Role.query.get(rid)
        # 获取要分配的权限
        mids = request.get_json().get('mids')
        # 清空当前角色的所有权限
        role.menus = []
        # 遍历要分配的权限
        mids = mids.split(',')
        for m in mids:
            if m: # 判断m是否为空
                # 获取权限
                menu = models.Menu.query.get(int(m))
                # 给角色分配权限
                role.menus.append(menu)
        # 保存到数据库
        db.session.commit()
        # 返回结果
        return {'status': 200, 'msg': '分配权限成功'}
    except Exception as e:
        return {'status': 500, 'msg': '分配权限失败'}