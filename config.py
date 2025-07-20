import os

class Config:
    # 设置参数
    MYSQL_DIALECT = 'mysql'
    MYSQL_DRIVER = 'pymysql'
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = '123'
    MYSQL_HOST = '192.168.31.152' # localhost/127.0.0.1
    MYSQL_PORT = 3306
    MYSQL_DB = 'flask_shop'
    MYSQL_CHARSET = 'utf8mb4'

    # 数据库链接字符串URI
    SQLALCHEMY_DATABASE_URI = f'{MYSQL_DIALECT}+{MYSQL_DRIVER}://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset={MYSQL_CHARSET}'
    # 数据盐
    SECRET_KEY = os.urandom(16)
    # 设置JSON数据不使用ASCII编码
    JSON_AS_ASCII = False
    RESTFUL_JSON = {'ensure_ascii': False}
    # 设置token的过期时间,秒为单位
    JWT_EXPIRATION_DELTA = 60 * 60 * 24
    # 设置可以上传的图片类型
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    # 获取当前项目的根路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 设置图片上传的路径
    UPLOAD_FOLDER = os.path.join(BASE_DIR,'flask_shop', 'static/upload')
    
class DevelopmentConfig(Config):
    # 开发环境
    # DEBUG模式
    DEBUG = True

class ProductionConfig(Config):
    # 生产环境
    DEBUG = False

class TestingConfig(Config):
    # 测试环境
    pass

config_map = {
    'develop': DevelopmentConfig, # 开发环境
    'product': ProductionConfig, # 生产环境
    'test': TestingConfig # 测试环境
}