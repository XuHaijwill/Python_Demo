'''
1. 要加密的数据
    userid
2. 加密的算法
    pip install pyjwt==2.6.0
3. 加密的密钥
    SECRET_KEY
'''
import time
from functools import wraps

from flask import request
import jwt
from flask import current_app

# 生成token
def generate_token(data):
    '''
    data: 要加密的数据,数据类型是字典
    '''
    # 设置数据的过期时间
    data.update({'exp': time.time()+current_app.config['JWT_EXPIRATION_DELTA']})
    # 数据的加密
    token = jwt.encode(data, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

# 解密token
def verify_token(token):
    # 数据的解密
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except Exception as e:
        return None
    return data


def login_required(view_func):
    @wraps(view_func)
    def verify_token_info(*args, **kwargs):
        # 获取用户传递来的token
        token = request.headers.get('token')
        print(token)
        # 解析 token
        if verify_token(token):
            return view_func(*args, **kwargs)
        else:
            return {'status': 401, 'msg': 'token 无效'}
        # 返回函数
    return verify_token_info