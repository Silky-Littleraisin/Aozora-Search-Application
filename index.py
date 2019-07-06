import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .db import get_db

bp=Blueprint('index',__name__,url_prefix='/index')


@bp.route('/',methods=('GET','POST'))
def homepage():
    if request.method=='POST':
        keyword=request.form['singleInput']
        return redirect(url_for('search.result',keyword=keyword))
    return render_template('index/homepage.html')

@bp.route('/ajax',methods=('GET',))
def homepage_ajax():

    return render_template('index/homepage.html')
