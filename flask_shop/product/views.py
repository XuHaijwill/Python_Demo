import hashlib
from time import time

from flask_restful import Resource,reqparse
from flask import request,current_app

from flask_shop import models
from flask_shop.product import product_api,product_bp
from flask_shop import db

class Products(Resource):
    def post(self):
        '''
        增加商品
        '''
        try:
            # 创建参数解析器
            parser = reqparse.RequestParser()
            # 添加参数
            parser.add_argument('name', type=str, required=True, help='商品名称不能为空')
            parser.add_argument('price', type=float, help='商品价格不能为空')
            parser.add_argument('number',type=int)
            parser.add_argument('introduce',type=str)
            parser.add_argument('weight',type=int)
            parser.add_argument('cid_one',type=int)
            parser.add_argument('cid_two',type=int)
            parser.add_argument('cid_three',type=int)

            parser.add_argument('pics',type=list,location='json')
            parser.add_argument('attr_static',type=list,location='json')
            parser.add_argument('attr_dynamic',type=list,location='json')
        
            # 解析参数
            args = parser.parse_args()
            # 创建商品对象
            product = models.Product(
                name=args.get('name'),
                price=args.get('price'),
                number=args.get('number'),
                introduce=args.get('introduce'),
                weight=args.get('weight'),
                cid_one=args.get('cid_one'),
                cid_two=args.get('cid_two'),
                cid_three=args.get('cid_three'),
                )
            # 添加商品
            db.session.add(product)
            db.session.commit()

            # 增加商品的图片
            for p in args.get('pics'):
                pic = models.Picture(path=p,pid=product.id)
                db.session.add(pic)
            # 增加商品的静态属性
            for a in args.get('attr_static'):
                attr =  models.ProductAttr(
                    pid=product.id,
                    aid=a.get('id'),
                    val=a.get('val'),
                    _type='static'
                    )
                db.session.add(attr)
            # 增加商品的动态属性
            for a in args.get('attr_dynamic'):
                attr =  models.ProductAttr(
                    pid=product.id,
                    aid=a.get('id'),
                    val=','.join(a.get('val')),
                    _type='dynamic'
                    )
                db.session.add(attr)
            # 提交事务
            db.session.commit()
            # 返回结果
            return {'status':200,'msg':'增加商品成功'}
        except Exception as e :
            return {'status':500,'msg':'增加商品失败'}
    
    def get(self):
        '''
        获取商品列表
        '''
        # 创建参数解析器
        parser = reqparse.RequestParser()
        # 添加参数
        parser.add_argument('name', type=str,location='args')
        # 解析参数
        args = parser.parse_args()
        # 获取参数
        name = args.get('name')
        # 根据name是否有值，来决定查询所有商品还是根据name查询商品
        if name:
            product_list = models.Product.query.filter(models.Product.name.like(f'%{name}%')).all()
        else:
            product_list = models.Product.query.all()
        return {
            'status':200,
            'msg':'获取商品列表成功',
            'data':[product.to_dict() for product in product_list]
        }
product_api.add_resource(Products,'/products/')

class Product(Resource):
    def delete(self,id):
        '''
        删除商品
        '''
        try:
            # 根据id查询商品
            product = models.Product.query.get(id)
            # 删除商品
            db.session.delete(product)
            # 提交事务
            db.session.commit()
            #  返回结果
            return {'status':200,'msg':'删除商品成功'}
        except Exception as e :
            return {
                'status':500,
                'msg':'删除商品失败'
            }
product_api.add_resource(Product,'/product/<int:id>/')

@product_bp.route('/upload_img/',methods=['POST'])
def upload_img():
    '''
    上传图片
    '''
    # 获取图片
    img_file =  request.files.get('file')
    # 判断图片是否存在
    if not img_file:
        return {'status':500,'msg':'图片不存在'}
    # 判断图片的类型是否是允许上传的类型
    if allowed_img(img_file.filename):
        # 获取图片的保存路径
        floder = current_app.config.get('UPLOAD_FOLDER')
        # 生成一个文件名
        file_name = md5_file() + '.' + img_file.filename.rsplit('.',1)[1]
        # 保存文件
        img_file.save(f'{floder}/{file_name}')
        # 封装数据
        data = {
            'path':f'/static/upload/{file_name}',
            'url':f'http://127.0.0.1:5000/static/upload/{file_name}'
        }
        # 返回结果
        return {'status':200,'msg':'上传图片成功','data':data}
    else:
        return {'status':500,'msg':'图片类型不允许上传'}

def allowed_img(filename):
    '''
    判断文件名是否为允许的文件类型
    :param filename: 文件名   1.png  aaa.jpg
    '''
    # if '.' in filename:
    #     # 获取文件的后缀
    #     suffix = filename.rsplit('.',1)[1]
    #     # 判断文件的后缀是否在允许的文件类型中
    #     if suffix in current_app.config.get('ALLOWED_EXTENSIONS'):
    #         return True
    #     return False
    # else:
    #     return False
    return '.' in filename and filename.rsplit('.',1)[1] in current_app.config.get('ALLOWED_EXTENSIONS')

def md5_file():
    '''
    通过md5算法，对时间戳加密，返回字符串
    '''
    # 创建hashlib对象
    md5 = hashlib.md5()
    # 获取当前时间戳
    timestamp = str(time())
    # 对时间戳进行加密
    md5.update(timestamp.encode())
    # 获取加密后的字符串
    file_name = md5.hexdigest()
    return file_name