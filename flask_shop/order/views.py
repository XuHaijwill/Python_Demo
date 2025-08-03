from flask_restful import Resource,reqparse

from flask_shop import models
from flask_shop.order import order_api

class Orders(Resource):
    def get(self):
        '''
        获取订单列表
        '''
        # 定义参数解析器
        parser = reqparse.RequestParser()
        # 添加参数
        parser.add_argument('name', type=str,location='args')
        # 解析参数
        args = parser.parse_args()
        # 获取参数
        name = args.get('name')
        # 根据参数查询数据
        if name:
            order_list = models.Order.query.filter(models.Order.name.like(f'%{name}%')).all()
        else:
            order_list = models.Order.query.all()
        
        return {
            'status':200,
            'msg':'获取订单列表成功',
            'data':[order.to_dict() for order in order_list]
        }

order_api.add_resource(Orders,'/orders/')

class Order(Resource):
    def get(self,id):
        '''
        获取订单详情
        '''
        order = models.Order.query.get(id)
        return {
            'status':200,
            'msg':'获取订单详情成功',
            'data':order.to_dict()
        }
order_api.add_resource(Order,'/order/<int:id>/') 


class Expresses(Resource):
    def get(self,id):
        '''
        获取快递列表
        :param id: 订单id
        '''
        express_list = models.Express.query.filter(models.Express.oid==id).order_by(models.Express.update_time.desc()).all()
        
        return {
            'status':200,
            'msg':'获取快递列表成功',
            'data':[express.to_dict() for express in express_list]
        }

order_api.add_resource(Expresses,'/expresses/<int:id>/')