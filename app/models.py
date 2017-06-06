# coding:utf-8
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from passlib.apps import custom_app_context as pwd_context
import config
from werkzeug.security import generate_password_hash


# 数据库映射文件

# 用户映射文件
class UserInfo(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(128), nullable=False, default="0")
    num = db.Column(db.Integer,default=0)
    last_login = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    # -----------------password加密 解密 token生成 验证-----------------------
    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password_hash):
        return pwd_context.verify(self.password, password_hash)

    def generate_testhome_token(self, expiration=3600):
        s = Serializer(config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'name': self.name})

    def verify_testhome_token(self, token):
        s = Serializer(config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return data['name'] == self.name


class ImageFile(db.Model):
    __tablename__ = 'ImageFile'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(30), index=True)
    position = db.Column(db.String(30), default="1")
    exist = db.Column(db.String(30), default="1")
    image = db.Column(db.LargeBinary(length=204800000))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class Log(db.Model):
    __tablename__ = 'Log'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(128))
    logtype = db.Column(db.String(128))
    action = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)


class Draw(db.Model):
    __tablename__ = 'Draw'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    url = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)


class ZmVedioZj(db.Model):
    __tablename__ = 'ZmVedioZj'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    comefrom = db.Column(db.String(128))
    image = db.Column(db.LargeBinary(length=204800000))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    zmvedios = db.relationship('ZmVedio', backref='zmvedio')


class ZmVedio(db.Model):
    __tablename__ = 'ZmVedio'
    id = db.Column(db.Integer, primary_key=True)
    zj_id = db.Column(db.Integer,db.ForeignKey('ZmVedioZj.id'))
    name = db.Column(db.String(128))
    vedio = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)