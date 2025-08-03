from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_shop import db

class BaseModel(object):  
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(db.Model,BaseModel):
    __tablename__ = 't_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True,nullable=False)
    pwd = db.Column(db.String(128))
    nick_name = db.Column(db.String(32))
    phone = db.Column(db.String(11))
    email = db.Column(db.String(32))
    
    # 建立用户与角色的关系多对1
    role_id = db.Column(db.Integer, db.ForeignKey('t_roles.id'))
    @property
    def password(self):
        return self.pwd

    @password.setter
    def password(self, pwd):
        # 数据密码数据加密
        self.pwd = generate_password_hash(pwd)

    def check_password(self, pwd):
        # 检查密码是否正确
        return check_password_hash(self.pwd, pwd)

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'nick_name':self.nick_name,
            'phone':self.phone,
            'email':self.email,
            'role_name':self.role.name if self.role else '',
            'role_id':self.role.id if self.role else '',
        }


trm = db.Table(
    't_roles_menus',
    db.Column('role_id', db.Integer, db.ForeignKey('t_roles.id')),
    db.Column('menu_id', db.Integer, db.ForeignKey('t_menus.id')),
)

class Menu(db.Model):
    __tablename__ = 't_menus'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True,nullable=False)
    path = db.Column(db.String(32))
    level = db.Column(db.Integer, default=1)

    pid = db.Column(db.Integer, db.ForeignKey('t_menus.id'))
    children = db.relationship('Menu')
    roles = db.relationship('Role', secondary=trm,backref='menus')
    def to_dict_tree(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'level': self.level,
            'pid': self.pid,
            'children': [child.to_dict_tree() for child in self.children]
        }
    def to_dict_list(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'level': self.level,
            'pid': self.pid,
        }

class Role(db.Model):
    __tablename__ = 't_roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), unique=True,nullable=False)
    desc = db.Column(db.String(128))

    # 建立角色与用户的关系1对多
    users = db.relationship('User', backref='role')
    # menus = db.relationship('Menu', secondary=trm)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc,
            # 'menus':[m.to_dict_list() for m in self.menus],
            # 'menus':[m.to_dict_tree() for m in self.menus if m.level == 1]  不好用的
            'menus':self.get_menu_dict()
        }

    def get_menu_dict(self):
        # 创建一列表存储所有的菜单
        menu_list = []
        menus  = sorted(self.menus,key=lambda temp:temp.id)
        # 查询所有的一级菜单
        for m in menus:
            # 判断是否是一级菜单
            if m.level == 1:
                first_dict = m.to_dict_list()
                # 查询所有的二级菜单
                first_dict['children'] = []
                for m2 in self.menus:
                    # 判断是否是二级菜单，且二级菜单的pid是否等于一级菜单的id
                    if m2.level == 2 and m2.pid == m.id:
                        # 将二级菜单添加到一级菜单的children中
                        first_dict['children'].append(m2.to_dict_list())
                # 将一级菜单添加到列表中
                menu_list.append(first_dict)
        return menu_list
    
class Category(db.Model):
    __tablename__ = 't_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    level = db.Column(db.Integer, default=1)
    pid = db.Column(db.Integer, db.ForeignKey('t_category.id'))
    
    children = db.relationship('Category')
    attrs = db.relationship('Attribute', backref='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'pid': self.pid,
        }

class Attribute(db.Model):
    __tablename__ = 't_attribute'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    val = db.Column(db.String(255))
    _type = db.Column(db.Enum('static','dynamic'))

    cid = db.Column(db.Integer, db.ForeignKey('t_category.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'val': self.val,
            'type': self._type,
            'cid': self.cid,
        }
    
class Product(db.Model):
    __tablename__ = 't_product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(512), nullable=False)
    price = db.Column(db.Float, default=0)
    number = db.Column(db.Integer, default=0)
    introduce = db.Column(db.Text) # 商品介绍
    big_img = db.Column(db.String(255)) # 商品大图
    small_img = db.Column(db.String(255)) # 商品小图
    state = db.Column(db.Integer) #0未通过 1审核中 2已通过
    is_promote = db.Column(db.Integer) # 是否促销
    hot_number = db.Column(db.Integer) # 热度
    weight = db.Column(db.Integer) # 权重

    cid_one = db.Column(db.Integer, db.ForeignKey('t_category.id'))
    cid_two = db.Column(db.Integer, db.ForeignKey('t_category.id'))
    cid_three = db.Column(db.Integer, db.ForeignKey('t_category.id'))

    category = db.relationship('Category', foreign_keys=[cid_three])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'number': self.number,
            'introduce': self.introduce,
            'big_img': self.big_img,
            'small_img': self.small_img,
            'state': self.state,
            'is_promote': self.is_promote,
            'hot_number': self.hot_number,
            'weight': self.weight,
            'cid_one': self.cid_one,
            'cid_two': self.cid_two,
            'cid_three': self.cid_three,
            'category': [a.to_dict() for a in self.category.attrs],
        }
    
class Picture(db.Model):
    __tablename__ = 't_picture'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255))
    pid = db.Column(db.Integer, db.ForeignKey('t_product.id'))

class ProductAttr(db.Model):
    __tablename__ = 't_product_attr'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Integer, db.ForeignKey('t_product.id'))
    aid = db.Column(db.Integer, db.ForeignKey('t_attribute.id'))
    val = db.Column(db.String(256))
    _type = db.Column(db.Enum('static','dynamic'))

class Order(db.Model,BaseModel):
    __tablename__ = 't_order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float, default=0)
    number = db.Column(db.Integer, default=0)
    pay_status = db.Column(db.Integer, default=0)  # 0 未支付 1 已支付
    is_send = db.Column(db.Integer, default=0)  # 0 未发货 1 已发货
    fapiao_title = db.Column(db.String(255))
    fapiao_content = db.Column(db.String(255))
    address = db.Column(db.String(255))
    uid = db.Column(db.Integer, db.ForeignKey('t_users.id'))
    
    user = db.relationship('User', foreign_keys=[uid])
    order_detail = db.relationship('OrderDetail', backref='order')
    express = db.relationship('Express', backref='order')

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'number': self.number,
            'pay_status': self.pay_status,
            'is_send': self.is_send,
            'fapiao_title': self.fapiao_title,
            'fapiao_content': self.fapiao_content,
            'address': self.address,
            'uid': self.uid,
            'user': self.user.nick_name,
        }

class OrderDetail(db.Model):
    '''订单详情表'''
    __tablename__ = 't_order_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oid = db.Column(db.Integer, db.ForeignKey('t_order.id'))
    pid = db.Column(db.Integer, db.ForeignKey('t_product.id'))
    number = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'oid': self.oid,
            'pid': self.pid,
            'number': self.number,
            'price': self.price,
            'total_price': self.total_price,
        }
class Express(db.Model):
    '''快递表'''
    __tablename__ = 't_express'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oid = db.Column(db.Integer, db.ForeignKey('t_order.id'))
    content = db.Column(db.String(256))
    update_time = db.Column(db.String(256))

    def to_dict(self):
        return {
            'id': self.id,
            'oid': self.oid,
            'content': self.content,
            'update_time': self.update_time,
        }