#-*- coding: utf-8 -*-
import os
import time, uuid, datetime
from flask import render_template, send_from_directory, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask import Markup, request, make_response
from app import app, db
from forms import PageInfo, BulletinForm, LoginForm, RegistrationForm,\
    PasswordResetRequestForm, PasswordResetForm, RentForm, DemandForm,ChangePasswordForm, ChangeUsernameForm
from DB import orm
from Utils import Util
from Logic import restful, logic
from .email import send_email
from datetime import datetime
from wtforms import ValidationError
from Parsing import page_parsing
import json

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
a = 1
@app.route('/bd/web/<path:path>')
def rootDir_web(path):
    index_key = path.rfind('py')
    if index_key > (len(path)-4):
        return redirect(url_for('view_rents'))
    return send_from_directory(os.path.join(app.root_path, '.'), path)


UPLOAD_PATH = 'E:\Python\Graduation_design\web\static'


@app.before_request
def before_request():
    if current_user.is_authenticated() and current_user.is_anonymous() is False:
        current_user.ping()
        if not current_user.confirmed and request.endpoint and request.endpoint[:4] == 'view' and request.endpoint != 'static':
            return redirect(url_for('unconfirmed'))


@app.route('/')
def rootDir():
    return redirect(url_for('login'))


@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('view_rent'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('view_rent'))
        if user.reset_password(token, form.password.data):
            flash(u'您的密码已经更新.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('view_rent'))
    return render_template('auth/reset_password.html', form=form)


@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('view_rent'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = orm.User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, u'重置密码',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash(u'已经发送了一封邮件到您的邮箱中，请确认')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('view_rent'))
    if current_user.confirm(token):
        flash(u'您已经激活了您的账户')
    else:
        flash(u'链接已失效')
    return redirect(url_for('view_rent'))


@app.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'已经发送了一封邮件到您的邮箱中，请确认')
    return redirect(url_for('view_rent'))


@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() is True or current_user.confirmed:
        return redirect(url_for('view_rents'))
    form = PageInfo()
    logic.LoadBasePageInfo('账户未激活', form)
    return render_template('auth/unconfirmed.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = orm.User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('view_rents'))
        flash(u'用户名或密码错误')
    elif request.method =='GET':
        logic.LoadBasePageInfo('登录',form)
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经退出登录.')
    return redirect(url_for('login'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    logic.LoadBasePageInfo('更改密码', form)
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            orm.User.query.filter_by(id=current_user.id).update({'password_hash':current_user.password_hash})
            orm.db.session.commit()
            flash('密码已经更改')
            return redirect(url_for('login'))
        else:
            flash('密码错误')
    return render_template("auth/change_password.html", form=form)


@app.route('/change-username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    logic.LoadBasePageInfo('更改昵称', form)
    if form.validate_on_submit():
        current_user.username=form.username.data
        orm.User.query.filter_by(id=current_user.id).update({'username':form.username.data})
        orm.db.session.commit()
        flash('用户名已经更改')
        return redirect(url_for('login'))
    return render_template("auth/change_username.html", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.user_type.data == '0':
            role = 2
        else:
            role = 3
        user = orm.User(email=form.email.data, username=form.username.data, password=form.password.data, role_id = role)
        token = user.generate_confirmation_token()
        try:
            send_email(user.email, 'Confirm Your Account',
                       'auth/email/confirm', user=user, token=token)
        except Exception:
            flash(u'邮件发送失败.')
            return redirect(url_for('register'))
        else:
            db.session.add(user)
            db.session.commit()
            flash(u'已经向您的邮箱那个发送了一份邮件.')
            return redirect(url_for('login'))
    elif request.method == 'GET':
        logic.LoadBasePageInfo('注册', form)
    return render_template('auth/register.html', form=form)


@app.route('/bd/view_demand', methods=['GET', 'POST'])
@login_required
def view_demand():
    demand_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_demands', page=1, q=q))
    form = DemandForm(request.form)
    form.area_id.choices = logic.g_choices_area
    form.subway_line.choices = logic.g_choices_subway
    form.mode_id.choices = logic.g_choices_mode
    if request.method == 'POST' and form.validate_on_submit():
        if form.id.data:
            demand = orm.Demand.query.get(int(form.id.data))
            demand.contacts = form.contacts.data
            demand.phone_number = form.phone_number.data
            demand.description = form.description.data
            demand.price_low = form.price_low.data
            demand.price_high = form.price_high.data
            demand.area_id = form.area_id.data
            demand.subway_line = form.subway_line.data
            demand.decorate_type = form.decorate_type.data
            demand.mode_id = form.mode_id.data
            demand.title = form.title.data
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
            return redirect(url_for('view_demands'))
        else:
            if form.decorate_type.data == '0':
                form.decorate_type.data = True
            else:
                form.decorate_type.data = False

            demand = orm.Demand(form.price_low.data, form.price_high.data, form.area_id.data,form.contacts.data,
                                form.phone_number.data, form.mode_id.data, form.decorate_type.data,
                                form.subway_line.data, form.description.data, now, form.title.data, current_user.id)
            orm.db.session.add(demand)
            try:
                orm.db.session.commit()
            except :
                orm.db.session.rollback()
            form.id.data = demand.id
            return redirect(url_for('view_demands'))
    elif request.method == 'GET' and demand_id:
        form = logic.GetDemandFormById(demand_id)
        logic.LoadBasePageInfo('修改求租信息', form)
    else:
        logic.LoadBasePageInfo('新建求租信息', form)
    return render_template('view_demand.html', form=form)


@app.route('/bd/view_demands', methods=['GET', 'POST'])
def view_demands():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    pagination = orm.Demand.query.order_by(orm.Demand.date.desc()).paginate(page, 10)
    count = orm.Demand.query.count()
    paging=get_pages(page,count,10)
    demands = pagination.items
    if request.method == 'POST':
        form = DemandForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.Demand.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_demands', page=page, q=q, paging=paging))
    form = PageInfo()
    logic.LoadBasePageInfo('所有求租信息', form)

    return render_template('view_demands.html', demands=demands, pagination=pagination, page=page, form=form, paging=paging)


@app.route('/bd/rent', methods=['GET', 'POST'])
def view_subway():
    page = request.args.get('page', 1, type=int)
    subway_id = request.args.get('subway_id')
    area_id = request.args.get('area_id')
    q = request.args.get('q')
    form = PageInfo()
    if subway_id:
        rents = orm.Rent.query.filter_by(subway_line = int(subway_id)).all()
        logic.LoadBasePageInfo(orm.Subway.query.filter_by(id=int(subway_id)).all()[0].name + '附近出租信息', form)
    elif area_id:
        rents = orm.Rent.query.filter_by(area_id=int(area_id)).all()
        logic.LoadBasePageInfo(orm.Area.query.filter_by(id=int(area_id)).all()[0].name + '出租信息', form)
    for rent in rents:
        if rent.rentimages != []:
            rent.rentimages.file = rent.rentimages[0].file
        else:
            rent.rentimages.file = 'notfound.png'
    if request.method == 'POST':
        form = RentForm(request.form)
    return render_template('view_rents.html', rents=rents, page=page, form=form)


@app.route('/bd/view_rent', methods=['GET', 'POST'])
@login_required
def view_rent():
    rent_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_rents', page=1, q=q))
    form = RentForm(request.form)
    form.area_id.choices = logic.g_choices_area
    form.residential_id.choices = logic.g_choices_residential
    form.subway_line.choices = logic.g_choices_subway
    form.mode_id.choices = logic.g_choices_mode
    if request.method == 'POST' and form.validate():
        if form.id.data:
            rent = orm.Rent.query.get(int(form.id.data))
            rent.title = form.title.data
            rent.area_id = form.area_id.data
            rent.description = form.description.data
            rent.price = form.price.data
            rent.mode_id = form.mode_id.data
            rent.rent_type = form.rent_type.data
            rent.contacts = form.contacts.data
            rent.phone_number = form.phone_number.data
            rent.size = form.size.data
            rent.address = form.address.data
            rent.decorate_type = form.decorate_type.data
            rent.residential_id = form.residential_id.data
            rent.subway_line = form.subway_line.data
            if request.form.has_key('upload'):
                file = request.files['image']
                if file:
                    file_server = str(uuid.uuid1()) + Util.file_extension(file.filename)
                    pathfile_server = os.path.join(UPLOAD_PATH, file_server)
                    file.save(pathfile_server)
                    if os.stat(pathfile_server).st_size < 1 * 1024 * 1024:
                        rentimage = orm.Rentimage(rent.id, file_server)
                        orm.db.session.merge(rentimage)  # merge 方法代替save
                        orm.db.session.commit()
                    else:
                        os.remove(pathfile_server)
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
            return redirect(url_for('view_rents'))
        else:
            if form.decorate_type.data == '0':
                form.decorate_type.data = True
            else:
                form.decorate_type.data = False
            rent = orm.Rent(form.area_id.data, form.title.data, form.price.data, form.description.data,
                            form.rent_type.data, form.mode_id.data, form.contacts.data, form.phone_number.data,
                            now, form.residential_id.data, form.size.data, form.address.data, form.decorate_type.data,
                            form.subway_line.data, current_user.id)
            orm.db.session.add(rent)
            # try:
            orm.db.session.commit()
            # except:
            #     orm.db.session.rollback()
            form.id.data = rent.id
            if request.form.has_key('upload'):
                file = request.files['image']
                if file:
                    file_server = str(uuid.uuid1()) + Util.file_extension(file.filename)
                    pathfile_server = os.path.join(UPLOAD_PATH, file_server)
                    file.save(pathfile_server)
                    if os.stat(pathfile_server).st_size < 1 * 1024 * 1024:
                        rentimage = orm.Rentimage(rent.id, file_server)
                        orm.db.session.merge(rentimage)  # merge 方法代替save
                        orm.db.session.commit()
                    else:
                        os.remove(pathfile_server)
            else:
                return redirect(url_for('view_rents'))
    elif request.method == 'GET' and rent_id:
        form = logic.GetRentFormById(rent_id)
        logic.LoadBasePageInfo('修改出租信息', form)
    else:
        logic.LoadBasePageInfo('新建出租信息', form)
    if form.id.data:
        rent = orm.Rent.query.get(int(form.id.data))
        form.rent = rent
        if form.rent and form.rent.rentimages != [] :
            form.images = [image.file for image in form.rent.rentimages]
    return render_template('view_rent.html', form=form)


@app.route('/bd/my_demand_publish',methods=['GET', 'POST'])
def my_demand_publish():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    demands = orm.Demand.query.filter_by(author_id=current_user.id).paginate(page,10).items
    count = orm.Demand.query.filter_by(author_id=current_user.id).count()
    paging = get_pages(page, count, 10)
    form = PageInfo()
    logic.LoadBasePageInfo('我的发布', form)
    return render_template('view_demands.html', demands=demands, form=form, paging=paging,url='/bd/my_demand_publish')


@app.route('/bd/my_rent_publish',methods=['GET', 'POST'])
def my_rent_publish():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    rents = orm.Rent.query.filter_by(author_id=current_user.id).paginate(page,5).items
    count = orm.Rent.query.filter_by(author_id=current_user.id).count()
    paging = get_pages(page, count, 5)
    for rent in rents:
        if rent.rentimages != []:
            rent.rentimages.file = rent.rentimages[0].file
        else:
            rent.rentimages.file = 'notfound.png'
    form = PageInfo()
    logic.LoadBasePageInfo('我的发布', form)
    return render_template('view_rents.html',rents=rents,form=form,paging=paging,url='/bd/my_rent_publish')


@app.route('/view_demand',methods=['GET', 'POST'])
def view_demand_int():
    demand_id = request.args.get('id')
    demands = orm.Demand.query.filter_by(id=int(demand_id)).all()
    form = PageInfo()
    logic.LoadBasePageInfo('求租信息', form)
    return render_template('demand.html', form=form, demands=demands)


@app.route('/view_rent',methods=['GET', 'POST'])
@login_required
def view_rent_int():
    if current_user.id:
        user_id = current_user.id
    like_rent_id = request.form.get('like_rent_id')
    unlike_rent_id = request.form.get('unlike_rent_id')
    if like_rent_id:
        rent_id = int(like_rent_id)
        results = orm.Like.query.filter_by(user_id=user_id, rent_id=rent_id).all()
        if len(results) == 0:
            like = orm.Like(user_id, rent_id)
            orm.db.session.add(like)
            orm.db.session.commit()
            form = PageInfo()
            logic.LoadBasePageInfo('出租信息', form)
            return render_template('rent.html', form=form,like=True)
    if unlike_rent_id:
        rent_id = int(unlike_rent_id)
        result = orm.Like.query.filter_by(user_id=user_id, rent_id=rent_id).one()
        orm.db.session.delete(result)
        orm.db.session.commit()
        form = PageInfo()
        logic.LoadBasePageInfo('出租信息', form)
        return render_template('rent.html', form=form, like=False)
    if request.method == 'GET':
        rent_id = request.args.get('id')
        rents = orm.Rent.query.filter_by(id=int(rent_id)).all()
        times = orm.Rent.query.filter_by(id=rent_id).one().times
        times += 1
        orm.Rent.query.filter_by(id=rent_id).update({'times':times})
        orm.db.session.commit()
        for rent in rents:
            if rent.rentimages != []:
                rent.rentimages.file = rent.rentimages[0].file
            else:
                rent.rentimages.file = 'notfound.png'
        form = PageInfo()
        logic.LoadBasePageInfo('出租信息', form)
        if rent_id:
            result = orm.Like.query.filter_by(user_id=user_id, rent_id=int(rent_id)).all()
            if len(result) > 0:
                like = True
            else:
                like = False
            return render_template('rent.html', form=form, rents=rents, like=like)
        return render_template('rent.html', form=form, rents=rents)


@app.route('/bd/view_rents', methods=['GET', 'POST'])
def view_rents():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    p = request.args.get('price')
    subway_id = request.args.get('subway_id')
    area_id = request.args.get('area_id')
    price =int(p) if p else None
    form = PageInfo()
    total_count = orm.Rent.query.count()
    paging = get_pages(page,total_count,5)
    if request.method == 'POST':
        form = RentForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.Rent.query.get(int(form.id.data)))
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
            return redirect(url_for('view_rents', page=page, q=q, paging=paging))
    if subway_id:
        rents = orm.Rent.query.filter_by(subway_line=int(subway_id)).all()
        count = len(rents)
        paging = get_pages(page, count, 5)
        logic.LoadBasePageInfo(orm.Subway.query.filter_by(id=int(subway_id)).all()[0].name + '附近出租信息', form)
        rent_image(rents)
        return render_template('view_rents.html', rents=rents, page=page, form=form,paging=paging)
    elif area_id:
        rents = orm.Rent.query.filter_by(area_id=int(area_id)).all()
        count = len(rents)
        paging = get_pages(page, count, 5)
        logic.LoadBasePageInfo(orm.Area.query.filter_by(id=int(area_id)).all()[0].name + '出租信息', form)
        rent_image(rents)
        return render_template('view_rents.html', rents=rents, page=page, form=form,paging=paging)
    else:
        if p is None:
            pagination = orm.Rent.query.order_by(orm.Rent.times.desc()).paginate(page,5)
            logic.LoadBasePageInfo('所有出租信息', form)
        elif price == 600:
            pagination = orm.Rent.query.filter(orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('600元以下所有出租信息', form)
        elif price == 1000:
            pagination = orm.Rent.query.filter(600 < orm.Rent.price , orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('600-1000元所有出租信息', form)
        elif price == 1500:
            pagination = orm.Rent.query.filter(1000 < orm.Rent.price, orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('1000-1500元所有出租信息', form)
        elif price == 2000:
            pagination = orm.Rent.query.filter(1500 < orm.Rent.price, orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('1500-2000元所有出租信息', form)
        elif price == 3000:
            pagination = orm.Rent.query.filter(2000 < orm.Rent.price, orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('2000-3000元所有出租信息', form)
        elif price == 5000:
            pagination = orm.Rent.query.filter(3000 < orm.Rent.price, orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('3000-5000元所有出租信息', form)
        elif price == 8000:
            pagination = orm.Rent.query.filter(5000 < orm.Rent.price, orm.Rent.price <= price).paginate(page, 5)
            logic.LoadBasePageInfo('5000-8000元所有出租信息', form)
        pagination_area = orm.Area.query.order_by(orm.Area.id).paginate(1,20)
        pagination_subway = orm.Subway.query.order_by(orm.Subway.id).paginate(1,20)
        # paginat
        rents = pagination.items
        areas = pagination_area.items
        subways = pagination_subway.items
        rent_image(rents)
        return render_template('view_rents.html', rents=rents, page=page, form=form, areas=areas, subways=subways,paging=paging)


@app.route('/bd/delete_image' , methods=['GET', 'POST'])
def delete_image():
    backurl = request.args.get('backurl', '/')
    print "backurl......",backurl
    file = request.args.get('file')
    if file:
        for x in orm.Rentimage.query.filter_by(file=file).all():
            orm.db.session.delete(x)
        for x in orm.Bulletinimage.query.filter_by(file=file).all():
            orm.db.session.delete(x)
        pathfile_server = os.path.join(UPLOAD_PATH, file)
        if os.path.exists(pathfile_server):
            os.remove(pathfile_server)
        orm.db.session.commit()
    return redirect(backurl)


@app.route('/view_bulletin',methods=['GET', 'POST'])
def view_bulletin_int():
    bulletin_id = request.args.get('id')
    bulletins = orm.Bulletin.query.filter_by(id=int(bulletin_id)).all()
    for bulletin in bulletins:
        if isinstance(bulletin.dt, datetime):
            bulletin.dt = bulletin.dt.strftime('%Y-%m-%d %H:%M:%S')
        if bulletin.bulletinimages != []:
            bulletin.bulletinimages.file = bulletin.bulletinimages[0].file
        else:
            bulletin.bulletinimages.file = 'notfound.png'
    form = PageInfo()
    logic.LoadBasePageInfo('新闻公告', form)
    return render_template('bulletin.html', form=form, bulletins=bulletins)


@app.route('/bd/view_bulletin' , methods=['GET', 'POST'])
def view_bulletin():
    bulletin_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_bulletins', page=1, q=q))

    form = BulletinForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.id.data:
            bulletin = orm.Bulletin.query.get(int(form.id.data))
            bulletin.title = form.title.data
            bulletin.content = form.content.data
            bulletin.source = form.source.data
            bulletin.dt = now
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
            return redirect(url_for('view_bulletins'))
        else:
            bulletin = orm.Bulletin(now, form.title.data, form.content.data, form.source.data, current_user.id)
            orm.db.session.add(bulletin)
            orm.db.session.commit()
            form.id.data = bulletin.id

        if request.form.has_key('upload'):
            file = request.files['image']
            if file :
                file_server = str(uuid.uuid1())+Util.file_extension(file.filename)
                pathfile_server = os.path.join(UPLOAD_PATH, file_server)
                file.save(pathfile_server)
                if os.stat(pathfile_server).st_size <1*1024*1024:
                    bulletinimage = orm.Bulletinimage(bulletin.id,file_server)
                    orm.db.session.merge(bulletinimage)
                    try:
                        orm.db.session.commit()
                    except:
                        orm.db.session.rollback()
                else:
                    os.remove(pathfile_server)
        else:
            return redirect(url_for('view_bulletin'))
    elif request.method =='GET' and bulletin_id:
        form = logic.GetBulletinFormById(bulletin_id)
        logic.LoadBasePageInfo('修改公告',form)
    else:
        logic.LoadBasePageInfo('新建公告', form)

    if form.id.data:
        bulletin = orm.Bulletin.query.get(int(form.id.data))
        form.bulletin = bulletin
        if form.bulletin:
            form.bulletinimages = form.bulletin.bulletinimages

    return render_template('view_bulletin.html',form = form)


@app.route('/bd/view_bulletins' , methods=['GET', 'POST'])
def view_bulletins():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    pagination = orm.Bulletin.query.order_by(orm.Bulletin.dt.desc()).paginate(page, 10)
    count = orm.Bulletin.query.count()
    paging = get_pages(page,count,10)
    bulletins = pagination.items
    for bulletin in bulletins:
        if isinstance(bulletin.dt,datetime):
            bulletin.dt = bulletin.dt.strftime('%Y-%m-%d %H:%M:%S')
        if bulletin.bulletinimages != []:
            bulletin.bulletinimages.file = bulletin.bulletinimages[0].file
        else:
            bulletin.bulletinimages.file = 'notfound.png'

    if request.method == 'POST':
        form = BulletinForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.Bulletin.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_bulletins', page=page, q=q, paging=paging))

    form = PageInfo()
    logic.LoadBasePageInfo('所有公告',form)

    return render_template('view_bulletins.html',bulletins = bulletins,form = form, pagination=pagination, page=page, paging=paging)


@app.route('/bd/view_accounts' , methods=['GET', 'POST'])
def view_accounts():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    pagination = orm.User.query.order_by(orm.User.id).paginate(page, 10)
    count = orm.User.query.count()
    paging=get_pages(page,count,10)
    users = pagination.items

    if request.method == 'POST':
        form = AccountForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.User.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_accounts', page=page, q=q, paging=paging))

    form = PageInfo()
    logic.LoadBasePageInfo('所有用户',form)

    return render_template('view_accounts.html', form=form, pagination=pagination, users=users, paging=paging)


@app.route('/bd/new_function', methods=['GET', 'POST'])
def new_funciton():
    page = request.args.get('page', 1, type=int)
    areas = orm.Area.query.order_by(orm.Area.id).paginate(page, 20).items
    form = PageInfo()
    logic.LoadBasePageInfo('房屋租金分布', form)
    if request.method == 'POST':
        area_id = request.form.get('area_id')
        area_id = int(area_id)
        global a
        a = json.dumps(area_id)
        area_name = orm.Area.query.filter_by(id=area_id).first().name
        series = [data for data in page_parsing.get_area_price(area_name)]
        return render_template('new_function.html', form=form, areas=areas)
    else:
        area_name = orm.Area.query.filter_by(id=a).first().name
        series = [data for data in page_parsing.get_area_price(area_name)]
        return render_template('new_function.html',form=form, areas=areas, area_id=a,area_name=area_name,series=series)


@app.route('/info', methods=['GET', 'POST'])
def info():
    form = PageInfo()
    logic.LoadBasePageInfo('个人信息', form)
    return redirect(url_for('change_username'))


@app.route('/my_favourite', methods=['GET', 'POST'])
def my_favourite():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    user_id = current_user.id
    rents = []
    favourite = []
    count = orm.Like.query.filter_by(user_id=user_id).count()
    for rent in orm.Like.query.filter_by(user_id=user_id).paginate(page,5).items:
        favourite.append(rent.rent_id)
    paging=get_pages(page,count,5)
    for rent in favourite:
        rents.append(orm.Rent.query.filter_by(id=rent).all()[0])
    form = PageInfo()
    logic.LoadBasePageInfo('我的收藏', form)
    for rent in rents:
        if rent.rentimages != []:
            rent.rentimages.file = rent.rentimages[0].file
        else:
            rent.rentimages.file = 'notfound.png'
    return render_template('view_rents.html', rents=rents, form=form,paging=paging,url='/my_favourite')


def rent_image(rents):
    for rent in rents:
        if rent.rentimages != []:
            rent.rentimages.file = rent.rentimages[0].file
        else:
            rent.rentimages.file = 'notfound.png'

def get_pages(page,count,unit):
    if count % unit != 0:
        total_pages = count / unit + 1
    else:
        total_pages = count / unit
    page_from = max(1, page - 5)
    page_to = min(total_pages, page + 5)
    return {'total_pages': total_pages, 'page': page, 'page_from': page_from, 'page_to': page_to}