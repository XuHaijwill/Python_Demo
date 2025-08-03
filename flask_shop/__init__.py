from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config_map

# 创建SQLAlchemy实例
db = SQLAlchemy()

def create_app(config_name):
    # 创建一个Flask实例
    app = Flask(__name__)
    # 根据config_name获取配置类
    Config = config_map.get(config_name)
    # 根据类来加载配置信息
    app.config.from_object(Config)
    # 初始化db
    db.init_app(app)

    # 获取user蓝图对象
    from flask_shop.user import user_bp
    # 注册蓝图
    app.register_blueprint(user_bp)

    # 获取menu蓝图对象
    from flask_shop.menu import menu_bp
    # 注册蓝图
    app.register_blueprint(menu_bp)

    # 获取role蓝图对象
    from flask_shop.role import role_bp
    # 注册蓝图
    app.register_blueprint(role_bp)

    # 获取category蓝图对象
    from flask_shop.category import cate_bp
    # 注册蓝图
    app.register_blueprint(cate_bp)

    # 获取attribute蓝图对象
    from flask_shop.category import attr_bp
    # 注册蓝图
    app.register_blueprint(attr_bp)

    # 获取product蓝图对象
    from flask_shop.product import product_bp
    # 注册蓝图
    app.register_blueprint(product_bp)

    # 获取order蓝图对象
    from flask_shop.order import order_bp
    # 注册蓝图
    app.register_blueprint(order_bp)
    return app