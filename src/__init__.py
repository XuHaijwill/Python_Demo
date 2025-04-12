# 初始化模板全局函数
from flask import Flask

from src.config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PyFly123'
    app.config.from_object(config[config_name])

    return app