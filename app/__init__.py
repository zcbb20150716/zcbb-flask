# coding: utf-8

from flask import Flask
from os import path
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from config import config
from werkzeug.routing import BaseConverter
from flask_nav import Nav
from flask_nav.elements import *

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

nav=Nav()
nav.register_element('top',Navbar(u'Flask入门',
                                    View(u'主页','home'),
                                    View(u'关于','about'),
                                    Subgroup(u'项目',
                                             View(u'项目一','about'),
                                             Separator(),
                                             View(u'项目二', 'service'),
                                    ),
))
basedir = path.abspath(path.dirname(__file__))
print basedir
db = SQLAlchemy()
bootstrap = Bootstrap()
babel = Babel()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.debug = True
    app.url_map.converters['regex'] = RegexConverter
    print app.url_map.converters
    app.config.from_object(config[config_name])
    db.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)
    nav.init_app(app)
    print nav.elems.get('top')

    from space import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint)
    print db
    return app
