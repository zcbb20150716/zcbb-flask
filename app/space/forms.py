# coding:utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length
import datetime


class searchForm(FlaskForm):
    start_year = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                             default=str(datetime.datetime.now()).split('-')[0])
    end_year = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                           default=str(datetime.datetime.now()).split('-')[0])
    start_month = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                              default=str(datetime.datetime.now()).split('-')[1])
    end_month = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                            default=str(datetime.datetime.now()).split('-')[1])
    start_day = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)], default='1')
    end_day = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)], default='2')
    submit = SubmitField(u'查询')


class codeReleaseForm(FlaskForm):
    startyear = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                            default=str(datetime.datetime.now()).split('-')[0])
    startmonth = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                             default=str(datetime.datetime.now()).split('-')[1])
    month = int(str(datetime.datetime.now()).split('-')[1])
    if month is 12:
        endyear = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                              default=str(int(str(datetime.datetime.now()).split('-')[0]) + 1))
        endmonth = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)], default='1')
    else:
        endyear = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                              default=str(datetime.datetime.now()).split('-')[0])
        endmonth = StringField(u'查询条件', validators=[DataRequired(), Length(1, 64)],
                               default="0" + str(int(str(datetime.datetime.now()).split('-')[1]) + 1))
    submit = SubmitField(u'查询')


class lyForm(FlaskForm):
    text = StringField(u'What is text?', validators=[DataRequired()])
    type = SelectField('类型', validators=[DataRequired()],
                         choices=[('0', '智能对话'), ('1', '播报天气')])
    submit = SubmitField(u'查询')


class imageForm(FlaskForm):
    name = StringField('Name')
    file = FileField('file')
    position = SelectField('类型', validators=[DataRequired()],
                         choices=[('1', '上边'), ('2', '下边'), ('3', '左边'), ('4', '右边')])
    exist = SelectField('是否展示', validators=[DataRequired()],
                           choices=[('1', '展示'), ('0', '不展示')])
    submit = SubmitField('submit')


class vediozjForm(FlaskForm):
    name = StringField('Name')
    comefrom = StringField('Comefrom')
    image_file = FileField('image_file')
    submit = SubmitField('submit')


class vedioForm(FlaskForm):
    name = StringField('Name')
    vedio_file = FileField('file')
    submit = SubmitField('submit')


class Permission():
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
