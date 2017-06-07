# coding:utf-8
import werkzeug
from flask import jsonify, session
from . import dashboard
from .forms import lyForm, imageForm, vediozjForm
from ..models import UserInfo, ImageFile, Log, Draw, ZmVedioZj, ZmVedio
from .. import db, babel
from config import LANGUAGES
from flask import request, render_template, redirect, make_response
import datetime
import time
import logging
import hashlib
import requests
import yaml
import base64
from ..tools import baidu_api as baidu
from ..tools import wx_api as wx


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


# -------------------------logging 日志统计--------------------------
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y %H:%M:%S',
                    filename='logs/pro.log', filemode='w')


@dashboard.route('/test')
def test():
    print 'success'
    return jsonify({'msg': 'success'})


@dashboard.route('/vue', methods=['GET'])
def vue_1():
    print str(datetime.datetime.now()) + '   vue_1 get request'
    response = jsonify({
        'data': {
            'message': 'hello',
            'info': u'欢迎'
        }
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@dashboard.route('/test2', methods=['GET', 'POST'])
def test2():
    if request.method == 'POST':
        print u"测试post接口"
        print request.form['size']
        print request.files
        print request.files['data'].read()
        print request.files['data'].stream.read()
        print u"成功...."
        return jsonify({'msg': 'success'})


@dashboard.route('/testing', methods=['GET', 'POST'])
def testing():
    if session.has_key("username"):
        if session['status'] == "9":
            return render_template('test/testing.html', u=session['username'], d=session['status'], title=u'测试接口')
        else:
            return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('404.html', title='404')


@dashboard.route('/', methods=['GET', 'POST'])
def center():
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if datas is not None:
            if int(time.time()) - datas.last_login < 500:
                return render_template('center.html', u=session['username'], d=session['status'], title=u'Zcbb-center')
            else:
                session.pop('username', None)
                return render_template('session.html', title=u'Zcbb-Welcome')
        else:
            return render_template('login.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/draw/<string:type>', methods=['GET', 'POST'])
def draw(type):
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            if session['status'] in ["1", "2", "9"]:
                _date = datetime.datetime.now()
                ds = Draw.query.all()
                create_log(session['username'], "draw", "/draw", _date)
                return render_template('draw.html', u=session['username'], ds=ds, type=type, d=session['status'], title='Zcbb-draw')
            else:
                return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/login', methods=['GET', 'POST'])
def login():
    _date = datetime.datetime.now()
    if request.method == 'POST':
        if session.has_key("username") and session['status'] in ["1", "2", "9"]:
            datas = UserInfo.query.filter_by(
                username=session['username']).first()
            if datas is not None:
                _num = datas.num + 1
                datas.num = datas.num + 1
                datas.last_login = int(time.time())
                db.session.add(datas)
                db.session.commit()
                create_log(session['username'], "login", "/login", _date)
                return render_template('index.html', u=session['username'], d=session['status'], num=_num,
                                       title='Zcbb-index')
            else:
                return render_template('wuxiao.html', title=u'Zcbb-Welcome-无效用户,请核实信息')
        else:
            username = request.form['username']
            password = request.form['password']
            if username in session and password in session:
                return render_template('index.html', u=session['username'], d=session['status'], title='Zcbb-index')
            if username is not None or password is not None:
                datas = UserInfo.query.filter_by(username=username).first()
                if datas is not None:
                    _num = datas.num + 1
                    datas.num = datas.num + 1
                    datas.last_login = int(time.time())
                    db.session.add(datas)
                    db.session.commit()
                    if datas is not None and werkzeug.security.check_password_hash(datas.password, password):
                        session['username'] = request.form['username']
                        session['password'] = request.form['password']
                        session['status'] = datas.__dict__['status']
                        if session['status'] is not None and session['status'] in ["1", "2", "9"]:
                            create_log(session['username'],
                                       "login", "/login", _date)
                            return render_template('index.html', u=session['username'], d=session['status'], num=_num, title='index')
                        else:
                            return render_template('shenhe.html', title=u'Zcbb-Welcome-账号审核中,请耐心等待')
                    else:
                        return render_template('wuxiao.html', title=u'Zcbb-Welcome-无效用户,请核实信息')
                else:
                    return render_template('wuxiao.html', title=u'Zcbb-Welcome-无效用户,请核实信息')
            else:
                return render_template('login.html', title=u'Zcbb-Welcome')
    return render_template('login.html', title=u'Welcome')


@dashboard.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        datas = UserInfo.query.filter_by(username=username).first()
        if datas is not None:
            return render_template('login.html', title=u'Zcbb-Welcome')
        else:
            if username is not None or password is not None:
                _date = datetime.datetime.now()
                user = UserInfo(username=username, password=password,
                                create_time=_date, update_time=_date)
                user.hash_password(password)
                db.session.add(user)
                db.session.commit()
                create_log(username, "regist", "/regist", _date)
                return render_template('shenhe.html', title=u'Zcbb-Welcome-账号审核中,请耐心等待')
            else:
                return render_template('register.html', title=u'Zcbb-register')
    return render_template('register.html', title=u'Zcbb-register')


@dashboard.route('/logout', methods=['GET', 'POST'])
def logout():
    _date = datetime.datetime.now()
    if session.has_key("username"):
        create_log(session['username'], "logout", "/logout", _date)
        session.pop('username', None)
        return render_template('login.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            if session['status'] == "9":
                return render_template('admin/admin.html', u=session['username'], d=session['status'], title='Zcbb-admin')
            else:
                return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/showphoto', methods=['GET'])
def showphoto():
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            if session['status'] in ["1", "2", "9"]:
                _date = datetime.datetime.now()
                ds = ImageFile.query.all()
                create_log(session['username'],
                           "showphoto", "/showphoto", _date)
                return render_template('showphoto.html', u=session['username'], ds=ds, d=session['status'], title='Zcbb-admin', base64=base64)
            else:
                return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showuser', methods=['GET', 'POST'])
def admin_showuser():
    datas = UserInfo.query.filter_by(username=session['username']).first()
    if int(time.time()) - datas.last_login < 500:
        if session.has_key("username") and session['status'] == "9":
            return redirect('dashboard/admin/showuser/info/1')
        elif session.has_key("username") and session['status'] != "9":
            return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        session.pop('username', None)
        return render_template('session.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showuser/info/<int:page>', methods=['GET', 'POST'])
def showuser(page):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = page
            pagination = UserInfo.query.filter(UserInfo.id > 0).paginate(
                page=_g, per_page=1, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showuser",
                       "/admin/showuser", _date)
            return render_template('admin/showuser.html',
                                   u=session['username'],
                                   d=session['status'],
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-用户管理')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showlog', methods=['GET', 'POST'])
def admin_showlog():
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            return redirect('dashboard/admin/showlog/info/1')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showlog/info/<int:page>', methods=['GET', 'POST'])
def showlog(page):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = page
            pagination = Log.query.filter(Log.id > 0).paginate(
                page=_g, per_page=10, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showlog", "/admin/showlog", _date)
            return render_template('admin/showlog.html',
                                   u=session['username'],
                                   d=session['status'],
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-日志管理')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showimage', methods=['GET', 'POST'])
def admin_showimage():
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            return redirect('dashboard/admin/showimage/info/1')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/showimage/info/<int:page>', methods=['GET', 'POST'])
def showimage(page):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = page
            pagination = Log.query.filter(Log.id > 0).paginate(
                page=_g, per_page=10, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showimage",
                       "/admin/showimage", _date)
            return render_template('admin/showimage.html',
                                   u=session['username'],
                                   d=session['status'],
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-图片管理')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/uploadphoto', methods=['GET', 'POST'])
def upload():
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            form = imageForm()
            if request.method == 'POST' and form.validate():
                file = request.files['file'].read()
                file_name = form.name.data
                position = form.position.data
                exist = form.exist.data
                image_file = ImageFile(image_name=file_name, image=file, position=position,
                                       exist=exist, create_time=_date, update_time=_date)
                print image_file
                db.session.add(image_file)
                db.session.commit()
                create_log(session['username'], "uploadphoto",
                           "/admin/uploadphoto", _date)
                return render_template('success.html', u=session['username'], d=session['status'])
            return render_template('admin/uploadphoto.html', u=session['username'], d=session['status'], form=form, base64=base64, title="Zcbb-uploadphoto")
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('404.html', title='error-404')


@dashboard.route('/admin/vediozj', methods=['GET', 'POST'])
def vediozj():
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            form = vediozjForm()
            if request.method == 'POST' and form.validate():
                image_file = request.files['image_file'].read()
                name = form.name.data
                _from = form.comefrom.data
                zmVedioZj = ZmVedioZj(
                    name=name, comefrom=_from, image=image_file, create_time=_date, update_time=_date)
                db.session.add(zmVedioZj)
                db.session.commit()
                create_log(session['username'], "vediozj",
                           "/admin/vediozj", _date)
                return render_template('success.html', u=session['username'], d=session['status'])
            return render_template('admin/vediozj.html', u=session['username'], d=session['status'], form=form, base64=base64, title="Zcbb-vediozj")
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('404.html', title='error-404')


@dashboard.route('/bofang/<int:num>', methods=['GET', 'POST'])
def bofang(num):
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            info = ZmVedio.query.filter_by(id=num).first()
            return render_template('bofang.html', info=info, u=session['username'], d=session['status'], title=u'Zcbb-index')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/admin/uploadvedio', methods=['GET', 'POST'])
def uploadvedio():
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        op = ZmVedioZj.query.filter(ZmVedioZj.id > 0)
        if int(time.time()) - datas.last_login < 500:
            if request.method == 'POST':
                vedio_file = request.form['vedio']
                name = request.form['name']
                zj_id = request.form['zj_id']
                zmVedio = ZmVedio(
                    name=name, zj_id=zj_id, vedio=vedio_file, create_time=_date, update_time=_date)
                db.session.add(zmVedio)
                db.session.commit()
                create_log(session['username'], "vedio", "/admin/vedio", _date)
                return render_template('success.html', u=session['username'], d=session['status'])
            return render_template('admin/vedio.html', u=session['username'], d=session['status'], op=op, base64=base64, title="Zcbb-vediozj")
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('404.html', title='error-404')


@dashboard.route('/showvediozj/info/<int:page>', methods=['GET', 'POST'])
def showvediozj(page):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = page
            pagination = ZmVedioZj.query.filter(ZmVedioZj.id > 0).paginate(
                page=_g, per_page=10, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showvediozj",
                       "/showvediozj", _date)
            return render_template('vediozj.html',
                                   u=session['username'],
                                   d=session['status'],
                                   base64=base64,
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-媒体分类')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/showvedio/info/<int:search>', methods=['GET', 'POST'])
def showvedio(search):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = 1
            pagination = ZmVedio.query.filter(ZmVedio.zj_id == search).paginate(
                page=_g, per_page=10, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showvedio", "/showvedio", _date)
            return render_template('vedio.html',
                                   u=session['username'],
                                   d=session['status'],
                                   base64=base64,
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-媒体分类')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/showvediozj/info/<string:search>', methods=['GET', 'POST'])
def vediosearch(search):
    _date = datetime.datetime.now()
    if session.has_key("username") and session['status'] == "9":
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            _g = 1
            pagination = ZmVedioZj.query.filter(ZmVedioZj.name.ilike('%' + search + '%')).paginate(
                page=_g, per_page=10, error_out=False)
            posts = pagination.items
            create_log(session['username'], "showvediozj",
                       "/showvediozj", _date)
            return render_template('vediozj.html',
                                   u=session['username'],
                                   d=session['status'],
                                   base64=base64,
                                   infos=posts,
                                   pagination=pagination,
                                   title=u'Zcbb-媒体分类')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    elif session.has_key("username") and session['status'] != "9":
        return render_template('403.html', u=session['username'], d=session['status'], title='error-403')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/index', methods=['GET', 'POST'])
def index():
    if session.has_key("username"):
        datas = UserInfo.query.filter_by(username=session['username']).first()
        if int(time.time()) - datas.last_login < 500:
            return render_template('index.html', u=session['username'], d=session['status'], title=u'Zcbb-index')
        else:
            session.pop('username', None)
            return render_template('session.html', title=u'Zcbb-Welcome')
    else:
        return render_template('login.html', title=u'Zcbb-Welcome')


@dashboard.route('/success', methods=['GET', 'POST'])
def success():
    if session.has_key("username"):
        return render_template('success.html', u=session['username'], d=session['status'], title=u'Zcbb-success')
    else:
        return render_template('404.html', title='error-404')


@dashboard.route('/ai', methods=['Get', 'Post'])
def get_baidu():
    _date = datetime.datetime.now()
    form = lyForm()
    if request.method == "POST":
        text = request.form['text']
        ai_type = form.type.data
        print 'logging::选择类型数据：数据为"""%s"""' % ai_type
        print 'logging::传入语音数据：数据为"""%s"""' % text
        if ai_type == "0":
            print get_date() + '调用图灵机器人api.....'
            d = {
                "timestamp": str(int(time.time())),
                "apiKey": "b0f010a62374422d923848e2420fe642",
                "secret": "968b64ab77a4e4cb",
                "cmd": text
            }
            r = requests.get(
                "http://127.0.0.1:8080/api/info/get_liaotianduihua", params=d)
            print "请求本地java-api返回data参数为：" + r.text

            h = {
                "content-type": "application/json"
            }

            _d = yaml.load(r.text)
            print "妆化后" + str(_d)
            p = requests.post(
                "http://www.tuling123.com/openapi/api", json=_d, headers=h)
            _r = yaml.load(p.text)
            _out = _r['text']
            if p.status_code == 200:
                print "调用成功..."
                _status = "success!!!"
                baidu.create_ai_file(_out, session['username'])
                print get_date() + '生成文件.....'
                print get_date() + '开始播放mp3'
                create_log(session['username'], "ai", "/ai", _date)
                _u = "http://zcbb.natapp4.cc/ai-" + \
                    session['username'] + ".mp3"
                return render_template('output.html', url=_u, form=form, out=_out, status=_status, u=session['username'], d=session['status'], title=u"Zcbb-智能机器人ai")
            else:
                print "调用失败..."
                _status = "fail!!!"
                create_log(session['username'], "ai", "/ai", _date)
                return jsonify({"msg": _status})
        elif ai_type == "1":
            print '进来了吗'
            _path, _text = baidu.create_weather_file(session['username'])
            print get_date() + '生成文件.....'
            print get_date() + '开始播放mp3'
            baidu.create_weather_file(session['username'])
            create_log(session['username'], "ai", "/ai", _date)
            _u = "http://zcbb.natapp4.cc/we-" + session['username'] + ".mp3"
            return render_template('output.html', url=_u, out=_text, status="success!!!", u=session['username'], d=session['status'], title=u"Zcbb-智能机器人ai")
        else:
            print ""
    return render_template('input.html', form=form, u=session['username'], d=session['status'], title=u"Zcbb-智能机器人ai")


@dashboard.route('/vedio', methods=['Post'])
def get_vedio():
    data = yaml.load(request.get_data())
    print request.url
    print data
    print data['serverId']
    token = wx.get_Token('wxca71f5a3e09e3df0',
                         '91e55d425f044670c10a37d9f6b875a0')
    media_id = data['serverId']
    _d = {
        "access_token": token,
        "media_id": media_id
    }
    url = "http://file.api.weixin.qq.com/cgi-bin/media/get"
    r = requests.get(url, params=_d)
    print r.text
    return jsonify({'msg': data})


@dashboard.route('/wx')
def wx():
    now = int(time.time())
    noncestr = '%s' % time.time()
    print '---------------'
    print noncestr
    print '---------------'
    base_url = "http://zcbb.natapp1.cc/flask/"
    url = base_url + request.url.split('/')[-1]
    url2 = url.decode('utf-8')
    print 'URL:::---------------'
    print url
    print url2
    print '---------------'
    jsapi_ticket = wx.get_jsapi_ticket('wxca71f5a3e09e3df0',
                                       '91e55d425f044670c10a37d9f6b875a0')  # 用户自定义函数，用于获取jsapi_ticket
    print jsapi_ticket
    signature = 'jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s' % (
        jsapi_ticket, noncestr, now, url2)
    m = hashlib.sha1()
    m.update(signature)
    signature = m.hexdigest()
    print 'signature::::' + signature
    signature = {"timestamp": now, "nonceStr": noncestr,
                 "signature": signature, "url": url}
    return render_template('wx.html', signature=signature)


def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


@dashboard.app_errorhandler(404)
def page_not_found(e):
    print e
    return render_template('404.html', u=session['username']), 404


@dashboard.app_errorhandler(500)
def server_interval(e):
    print e
    return render_template('500.html', u=session['username']), 500


def create_log(user, log_type, action, date):
    _u = UserInfo.query.filter_by(username=user).first()
    if _u is not None:
        _log = Log(user=user, logtype=log_type,
                   action=action, create_time=date)
        db.session.add(_log)
        db.session.commit()
