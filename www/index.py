#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
from imp import reload

from flask import (Flask, flash, redirect, render_template, request, session, url_for)

from SQLiteHelper import DBHelper

app = Flask(__name__)
app.secret_key = os.urandom(24)
reload(sys)


@app.route('/')
def web_home():
    if 'username' not in session:
        return render_template('login.html')
    page_context = {
        'currentUsername': session['username']
    }
    return render_template('home.html', page_context=page_context)

# 登陆
@app.route('/login', methods=['GET', 'POST'])
def web_login():
    if request.method == 'GET':
        return redirect(url_for('web_home'))
    if request.method == 'POST':
        name = request.form.get('username', None)
        password = request.form.get('password', None)
        if name.strip() == '' or password.strip() == '':
            # return redirect(url_for('web_home'))
            return render_template('login.html')

        session['username'] = name
        db = DBHelper()
        if db.has_user(name, password):
            page_context = {
                'currentUsername': name
            }
            return render_template('home.html', page_context=page_context)  # 返回用户页面
        else:
            return '用户名或密码错误'

# 用户自行注册
@app.route('/register', methods=['GET', 'POST'])
def web_register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('username', None)
        password = request.form.get('password', None)
        if name is None or password is None:
            return render_template('register.html')
        else:
            db = DBHelper()
            if name.strip() == '' or password.strip() == '':
                return render_template('register.html')
            flag = db.insert_user(name, password)
            if flag == True:
                return redirect(url_for('web_home'))
            else:
                flash("注册失败")
                return render_template('register.html')
                # data = {}
                # data['code'] = 401
                # data['data'] = ''
                # data['msg'] = '注册失败'
                # return json.dumps(data, ensure_ascii=False)

# 用户
@app.route('/user', methods=['GET'])
def web_user():
    if 'username' not in session:
        return render_template('login.html')
    page_context = {
        'currentUsername': session['username']
    }
    db = DBHelper()
    list = db.get_all_user_info()
    page_context = {
        'currentUsername': session['username'],
        'list': list
    }
    return render_template('user.html', page_context=page_context)

# 用户添加
@app.route('/user/add', methods=['GET', 'POST'])
def web_user_add():
    if 'username' not in session:
        return render_template('login.html')
    page_context = {
        'currentUsername': session['username']
    }
    if request.method == 'GET':
        return render_template('user-add.html', page_context=page_context)
    if request.method == 'POST':
        name = request.form.get('username', None)
        password = request.form.get('password', None)
        if name is None or name.strip() == '':
            flash('姓名不能为空')
        elif password is None or password.strip() == '':
            flash('密码不能为空')
        else:
            db = DBHelper()
            flag = db.insert_user(name, password)
            if flag == True:
                return redirect(url_for('web_user'))
            else:
                flash("添加失败")
        return render_template('user-add.html', page_context=page_context)


# 返回用户所有内容
@app.route('/content', methods=['GET'])
def web_content():
    if 'username' not in session:
        return render_template('login.html')
    db = DBHelper()
    list = db.get_content_by_username(session['username'])
    print(list)
    if list is None:
        return 'No list'
    page_context = {
        'currentUsername': session['username'],
        'list': list
    }
    return render_template('content.html', page_context=page_context)

# 添加内容
@app.route('/content/add', methods=['GET', 'POST'])
def web_content_add():
    if 'username' not in session:
        return render_template('login.html')
    if request.method == 'GET':
        page_context = {
            'currentUsername': session['username']
        }
        return render_template('add.html', page_context=page_context)
    if request.method == 'POST':
        db = DBHelper()
        title = request.form.get('title', None)
        content = request.form.get('content', None)
        tag = request.form.get('tag', None)
        # 有时添加数据库会出错
        if session['username']:
            if db.insert_content_by_username(session['username'], title, content, tag) is True:
                return redirect(url_for('web_content'))
            else:
                return '添加失败'
        else:
            return redirect(url_for('web_login'))


@app.route('/logout', methods=['GET'])
def quit():
    session.pop('username', None)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
