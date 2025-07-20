from flask_restful import Resource,reqparse
from flask import request

from flask_shop import models
from flask_shop import db
from flask_shop.category import cate_api,attr_api,cate_bp

class Categorys(Resource):
    def get(self):
        level = request.args.get('level')
        pnum = request.args.get('pnum')
        psize = request.args.get('psize')
        if level:
            level = int(level)
        else:
            level = 3
        # 获取所有的分类信息query对象
        base_query = models.Category.query.filter(models.Category.level == 1)
        # 判断是否传递了分页参数
        if all([pnum,psize]):
            # 分页查询
            cates = base_query.paginate(page=int(pnum),per_page=int(psize))
        else:
            # 查询所有的分类信息
            cates = base_query.all()
        # 定义一个列表，用于存储所有的分类信息
        cate_list = self.to_tree(cates,level)
        # # 遍历一级分类
        # for c in cates:
        #     first_dict = c.to_dict()
        #     # 获取一级分类下的所有二级分类
        #     first_dict['children'] = []
        #     # 遍历二级分类
        #     for sc in c.children:
        #         second_dict = sc.to_dict()
        #         # 获取二级分类下的所有三级分类
        #         second_dict['children'] = []
        #         # 遍历三级分类
        #         for tc in sc.children:
        #             third_dict = tc.to_dict()
        #             second_dict['children'].append(third_dict)
        #         first_dict['children'].append(second_dict)
        #     cate_list.append(first_dict)
        return {'status':200,'msg':'获取分类成功','data':cate_list}
    
    def to_tree(self,info:list,level):  # level=2
        # 定义一个空列表，用于存储所有的分类信息
        info_list = []
        # 遍历所有的分类信息
        for i in info:
            i_dict = i.to_dict()
            if i.level < level:
                # 获取一级分类下的所有二级分类
                i_dict['children'] = self.to_tree(i.children,level)
            info_list.append(i_dict)
        return info_list

    def post(self):
        try:
            # 创建一个ReuqestParser对象
            parser = reqparse.RequestParser()
            # 添加参数
            parser.add_argument('name', type=str, required=True)
            parser.add_argument('level', type=int, required=True)
            parser.add_argument('pid', type=int)
            # 解析参数
            args = parser.parse_args()
            # 判断pid是否传递
            if args.get('pid'):
                c = models.Category(name=args.get('name'), level=args.get('level'), pid=args.get('pid'))
            else:
                c = models.Category(name=args.get('name'), level=args.get('level'))
            # 保存到数据库
            db.session.add(c)
            db.session.commit()
            return {'status':200,'msg':'添加分类成功'}
        except Exception as e:
            print(e)
            return {'status':500,'msg':'添加分类失败'}

cate_api.add_resource(Categorys,'/categorys/')

class Attributes(Resource):
    def get(self):
         # 创建一个ReuqestParser对象
        parser = reqparse.RequestParser()
        # 添加参数
        parser.add_argument('cid', type=int, required=True,location='args')
        parser.add_argument('_type', type=str, required=True,location='args')
        # 解析参数
        args = parser.parse_args()
        # 根据cid获取分类信息
        cate = models.Category.query.get(args.get('cid'))
        # 获取分类下的所有属性信息
        attr_list = []
        # 根据_type获取对象的属性
        if args.get('_type') == 'static':
            attr_list = [a.to_dict() for a in cate.attrs if a._type == 'static']
        elif args.get('_type') == 'dynamic':
            attr_list = [a.to_dict() for a in cate.attrs if a._type == 'dynamic']
        return {'status':200,'msg':'获取属性成功','data':attr_list}
    def post(self):
        try:
            # 创建一个ReuqestParser对象
            parser = reqparse.RequestParser()
            # 添加参数
            parser.add_argument('name', type=str, required=True)
            parser.add_argument('val', type=str)
            parser.add_argument('_type', type=str, required=True)
            parser.add_argument('cid', type=int, required=True)
            # 解析参数
            args = parser.parse_args()
            # 判断val是否传递
            if args.get('val'):
                c = models.Attribute(name=args.get('name'), val=args.get('val'), _type=args.get('_type'), cid=args.get('cid'))
            else:
                c = models.Attribute(name=args.get('name'), _type=args.get('_type'), cid=args.get('cid'))
            # 保存到数据库
            db.session.add(c)
            db.session.commit()
            return {'status':200,'msg':'添加属性成功'}
        except Exception as e:
            print(e)
            return {'status':500,'msg':'添加属性失败'}

attr_api.add_resource(Attributes,'/attributes/')

class Attribute(Resource):
    def get(self,id):
        try:
            # 根据id获取属性信息
            attr = models.Attribute.query.get(id)
            return {'status':200,'msg':'获取属性成功','data':attr.to_dict()}
        except Exception as e:
            print(e)
            return {'status':500,'msg':'获取属性失败'}
    def put(self,id):
        try:
            attr = models.Attribute.query.get(id)
            # 创建一个ReuqestParser对象
            parser = reqparse.RequestParser()
            # 添加参数
            parser.add_argument('name', type=str)
            parser.add_argument('val', type=str)
            parser.add_argument('_type', type=str)
            parser.add_argument('cid', type=int)
            # 解析参数
            args = parser.parse_args()
            if args.get('name'):
                attr.name = args.get('name')
            if args.get('val'):
                attr.val = args.get('val')
            if args.get('_type'):
                attr._type = args.get('_type')
            if args.get('cid'):
                attr.cid = args.get('cid')
            # 保存到数据库
            db.session.commit()
            return {'status':200,'msg':'修改属性成功'}
        except Exception as e:
            print(e)
            return {'status':500,'msg':'修改属性失败'}
    def delete(self,id):
        try:
            # 根据ID获取属性信息
            attr = models.Attribute.query.get(id)
            # 删除属性信息
            db.session.delete(attr)
            # 提交到数据库
            db.session.commit()
            return {'status':200,'msg':'删除属性成功'}
        except Exception as e:
            print(e)
            return {'status':500,'msg':'删除属性失败'}

attr_api.add_resource(Attribute,'/attribute/<int:id>/')

from sqlalchemy import func,text 
@cate_bp.route('/cate_grup/')
def cate_grup():
    '''
    根据level获取分类分组信息
    '''
    # rs = db.session.query(models.Category.level,func.count(1)).group_by(models.Category.level).all()
    sql = 'select level,count(1) from t_category group by level' 
    # sqlalchemy.exc.ArgumentError: Textual SQL expression 'select level,count(1) fro...' should be explicitly declared as text('select level,count(1) f
    # 这个错误就是告诉我们sql用声明是一个text文本
    rs = db.session.execute(text(sql)).all()  # [(1,5),(2,20),(3,60)]
    data = {
        'name':'分类数量',
        'xAxis':[f'{r[0]}级分类' for r in rs],
        'series':[r[1] for r in rs]
    }
    return {'status':200,'msg':'获取数据成功','data':data}