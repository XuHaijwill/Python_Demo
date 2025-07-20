from flask import request
from flask_restful import Resource

from flask_shop.menu import menu_api
from flask_shop import models

class Menus(Resource):
    def get(self):
        # 获取前端页面要求的数据类型,list tree
        type_ = request.args.get('type_')
        # 根据type_决定以什么结构返回数据
        if type_ == 'tree':
            # 通过模型获取数据
            menu_list = models.Menu.query.filter(models.Menu.level == 1).all()
            menu_data = []
            # 遍历数据
            for m in menu_list:
                menu_data.append(m.to_dict_tree())
            return {'status':200,'msg':'获取菜单成功','data':menu_data}
        else:
            # 通过模型获取数据
            menu_list = models.Menu.query.filter(models.Menu.level != 0).all()
            menu_data = []
            # 遍历数据
            for m in menu_list:
                menu_data.append(m.to_dict_list())
            return {'status':200,'msg':'获取菜单成功','data':menu_data}

menu_api.add_resource(Menus,'/menus/')