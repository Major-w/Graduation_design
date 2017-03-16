#-*- coding: utf-8 -*-
import os
import time, uuid, datetime
from flask import render_template, send_from_directory, session, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask import Markup, request, make_response
from app import app, db
from forms import PageInfo, InstitutionForm, BulletinForm, AccountForm, LoginForm, RegistrationForm,\
    PasswordResetRequestForm, PasswordResetForm, RentForm, DemandForm
from DB import orm
from Utils import Util
from Logic import restful, logic
from .email import send_email
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

@app.route('/bd/web/<path:path>')
def rootDir_web(path):
    index_key = path.rfind('py')
    if index_key > (len(path)-4):
        return redirect(url_for('view_rents'))
    return send_from_directory(os.path.join(app.root_path, '.'), path)


UPLOAD_PATH = '/Users/kai/practice_flask/Graduation_design'


# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         # current_user.ping()
#         if not current_user.confirmed :
#             return redirect(url_for('unconfirmed'))


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
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('view_rents'))
    return render_template('auth/unconfirmed.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = orm.User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('view_rent'))
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
def view_demand():
    demand_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_demands', page=1, q=q))
    form = DemandForm(request.form)
    form.area_id.choices = logic.g_choices_area
    form.subway_line.choices = logic.g_choices_subway
    if request.method == 'POST' and form.validate():
        if form.id.data:
            demand = orm.Demand.query.get(int(form.id.data))
            demand.contacts = form.contacts.data
            demand.phone_number = form.phone_number.data
            demand.description = form.description.data
            demand.price_low = form.price_low.data
            demand.price_high = form.price_high.data
            demand.area_id = form.area_id.data
            demand.subway_line = form.subway_line.data
            demand.decoration_type = form.decoration_type.data
            demand.rental_mode = form.rental_mode.data
        else:
            if form.decorate_type.data == '0':
                form.decorate_type.data = True
            else:
                form.decorate_type.data = False
            demand = orm.Demand(form.price_low.data, form.price_high.data, form.area_id.data,form.contacts.data,
                                form.phone_number.data, form.rental_mode.data, form.decorate_type.data,
                                form.subway_line.dataform.description.data)
            orm.db.session.add(demand)
            try:
                orm.db.session.commit()
            except :
                orm.db.session.rollback()
            form.id.data = demand.id
    elif request.method == 'GET' and demand_id:
        form = logic.GetDemandFormById(demand_id)
        logic.LoadBasePageInfo('修改求租信息', form)
    else:
        logic.LoadBasePageInfo('新建求租信息', form)
    return render_template('view_demand.html', form=form)



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
    if request.method == 'POST' and form.validate():
        if form.id.data:
            rent = orm.Rent.query.get(int(form.id.data))
            rent.title = form.title.data
            rent.area_id = form.area_id.data
            rent.description = form.description.data
            rent.price = form.price.data
            rent.rental_mode = form.rental_mode.data
            rent.rent_type = form.rent_type.data
            rent.contacts = form.contacts.data
            rent.phone_number = form.phone_number.data
            rent.size = form.size.data
            rent.address = form.address.data
            rent.decorate_type = form.decorate_type.data
            rent.residential_id = form.residential_id.data
            rent.subway_line = form.subway_line.data
        else:
            if form.decorate_type.data == '0':
                form.decorate_type.data = True
            else:
                form.decorate_type.data = False
            rent = orm.Rent(form.area_id.data, form.title.data, form.price.data, form.description.data,
                            form.rent_type.data, form.rental_mode.data, form.contacts.data, form.phone_number.data,
                            today, form.residential_id.data, form.size.data, form.address.data, form.decorate_type.data, form.subway_line.data)
            orm.db.session.add(rent)
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
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
    return render_template('view_rent.html', form=form)


@app.route('/view_rent/<int:id>',methods=['GET', 'POST'])
def view_rent_int():
    pass


@app.route('/bd/view_rents', methods=['GET', 'POST'])
def view_rents():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    pagination = orm.Rent.query.order_by(orm.Rent.date.desc()).paginate(page,10)
    rents = pagination.items

    if request.method == 'POST':
        form = RentForm(request.form)
        if request.form.has_key('delete'):
            # for x in orm.Rentimage.query.filter_by(rent_id=int(form.id.data)).all():
            #     pathfile_server = os.path.join(UPLOAD_PATH, x.file)
            #     if os.path.exists(pathfile_server):
            #         os.remove(pathfile_server)
            orm.db.session.delete(orm.Rent.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_rents', page=page, q=q))

    form = PageInfo()
    logic.LoadBasePageInfo('所有求租信息',form)

    return render_template('view_rents.html', rents=rents, pagination=pagination, page=page, form=form)



@app.route('/bd/delete_image' , methods=['GET', 'POST'])
def delete_image():
    backurl = request.args.get('backurl', '/')
    print "backurl......",backurl
    file = request.args.get('file')
    if file:
        for x in orm.Schoolimage.query.filter_by(file=file).all():
            orm.db.session.delete(x)
        for x in orm.Institutionimage.query.filter_by(file=file).all():
            orm.db.session.delete(x)
        for x in orm.Bulletinimage.query.filter_by(file=file).all():
            orm.db.session.delete(x)
        pathfile_server = os.path.join(UPLOAD_PATH, file)
        if os.path.exists(pathfile_server):
            os.remove(pathfile_server)
        orm.db.session.commit()
    return redirect(backurl)



@app.route('/bd/view_institution' , methods=['GET', 'POST'])
def view_institution():
    institution_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_institutions', page=1, q=q))
    form = InstitutionForm(request.form)
    form.area_id.choices = logic.g_choices_area
    form.feature_ids.choices = logic.g_choices_feature
    form.agespan_id.choices = logic.g_choices_agespan
    form.feetype_id.choices = logic.g_choices_feetype
    form.timeopen.data = datetime.time(8,30)
    form.timeclose.data = datetime.time(22,00)
#    form.message = form.data
    if request.method == 'POST' and form.validate():
        if form.id.data:
            institution = orm.Institution.query.get(int(form.id.data))
            institution.name = form.name.data
            institution.agespan_id = form.agespan_id.data
            institution.area_id = form.area_id.data
            institution.address = form.address.data
            institution.location = form.location.data
            institution.website = form.website.data
            institution.telephone = form.telephone.data
            institution.feedesc = form.feedesc.data
            institution.timeopen = form.timeopen.data
            institution.timeclose = form.timeclose.data
            institution.feetype_id = form.feetype_id.data
            institution.longitude = form.longitude.data
            institution.latitude = form.latitude.data
            orm.db.session.commit()
        else:
            institution = orm.Institution(form.name.data, form.agespan_id.data, form.area_id.data, form.address.data, form.location.data, form.website.data, form.telephone.data, form.feedesc.data, form.timeopen.data, form.timeclose.data, form.feetype_id.data, form.longitude.data, form.latitude.data, None)
            orm.db.session.add(institution)
            orm.db.session.commit()
            form.id.data = institution.id

        logic.SetInstitutionFeatures(int(form.id.data),form.feature_ids.data)

        if request.form.has_key('upload'):
            file = request.files['image']
            if file :
                file_server = str(uuid.uuid1())+Util.file_extension(file.filename)
                pathfile_server = os.path.join(UPLOAD_PATH, file_server)
                file.save(pathfile_server)
                if os.stat(pathfile_server).st_size <1*1024*1024:
                    institutionimage = orm.Institutionimage(institution.id,file_server)
                    orm.db.session.merge(institutionimage)
                    orm.db.session.commit()
                else:
                    os.remove(pathfile_server)
        else:
            return redirect(url_for('view_institution'))
    elif request.method =='GET' and institution_id:
        form = logic.GetInstitutionFormById(institution_id)
        logic.LoadBasePageInfo('修改培训机构',form)
    else:
        logic.LoadBasePageInfo('新建培训机构',form)

    if form.id.data:
        institution = orm.Institution.query.get(int(form.id.data))
        form.institution = institution
        if form.institution:
            form.institutionimages = form.institution.institutionimages

    return render_template('view_institution.html',form = form)



@app.route('/bd/view_institutions' , methods=['GET', 'POST'])
def view_institutions():
    page = request.args.get('page', 1)
    q = request.args.get('q')
    institutions = restful.GetInstitutions(int(page),q)
    if not institutions.has_key(restful.ITEM_OBJECTS):
        return redirect(url_for('view_institutions'))

    institutionforms =[logic.GetInstitutionFormById(x[restful.ITEM_ID]) for x in institutions[restful.ITEM_OBJECTS]]
    while None in institutionforms:
        institutionforms.remove(None)


#    form.message = form.data
    if request.method == 'POST':
        form = InstitutionForm(request.form)
        if request.form.has_key('delete'):
            for x in orm.Institutionimage.query.filter_by(institution_id=int(form.id.data)).all():
                pathfile_server = os.path.join(UPLOAD_PATH, x.file)
                if os.path.exists(pathfile_server):
                    os.remove(pathfile_server)
            orm.db.session.delete(orm.Institution.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_institutions', page=page, q=q))

    form = PageInfo()
    logic.LoadBasePageInfo('所有出租信息',form)

    return render_template('view_institutions.html',forms = institutionforms,form = form, paging=restful.GetPagingFromResult(institutions))





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
            bulletin.dt = form.dt.data
            bulletin.title = form.title.data
            bulletin.content = form.content.data
            bulletin.source = form.source.data
            bulletin.author = form.author.data
            orm.db.session.commit()
        else:
            bulletin = orm.Bulletin(form.dt.data, form.title.data, form.content.data, form.source.data, form.author.data)
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
        form.dt.data = datetime.now()
        logic.LoadBasePageInfo('新建公告', form)

    if form.id.data:
        bulletin = orm.Bulletin.query.get(int(form.id.data))
        form.bulletin = bulletin
        if form.bulletin:
            form.bulletinimages = form.bulletin.bulletinimages

    return render_template('view_bulletin.html',form = form)



@app.route('/bd/view_bulletins' , methods=['GET', 'POST'])
def view_bulletins():
    page = request.args.get('page', 1)
    q = request.args.get('q')
    bulletins = restful.GetBulletins(int(page),q)
    if not bulletins.has_key(restful.ITEM_OBJECTS):
        return redirect(url_for('view_bulletins'))

    bulletinforms =[logic.GetBulletinFormById(x[restful.ITEM_ID]) for x in bulletins[restful.ITEM_OBJECTS]]
    while None in bulletinforms:
        bulletinforms.remove(None)

    if request.method == 'POST':
        form = BulletinForm(request.form)
        if request.form.has_key('delete'):
            for x in orm.Bulletinimage.query.filter_by(bulletin_id=int(form.id.data)).all():
                pathfile_server = os.path.join(UPLOAD_PATH, x.file)
                if os.path.exists(pathfile_server):
                    os.remove(pathfile_server)
            orm.db.session.delete(orm.Bulletin.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_bulletins', page=page, q=q))

    form = PageInfo()
    logic.LoadBasePageInfo('所有公告',form)

    return render_template('view_bulletins.html',forms = bulletinforms,form = form, paging=restful.GetPagingFromResult(bulletins))




@app.route('/bd/view_account' , methods=['GET', 'POST'])
def view_account():
    account_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_accounts', page=1, q=q))

    form = AccountForm(request.form)


    if request.method == 'POST' and form.validate():
        if form.id.data:
            account = orm.Account.query.get(int(form.id.data))
            account.username = form.telephone.data
            account.name = form.telephone.data
            account.telephone = form.telephone.data
            account.role = 0
            account.flag_telephone = 1 if form.flag_telephone.data else 0
            account.checkcode = form.checkcode.data
            account.source = form.source.data
            account.dtcreate = form.dtcreate.data
            orm.db.session.commit()
        else:
            account = orm.Account(form.telephone.data, '1234', form.telephone.data, form.telephone.data, 0, 1 if form.flag_telephone.data else 0, '1234', form.source.data, form.dtcreate.data)
            orm.db.session.add(account)
            try:
                orm.db.session.commit()
            except:
                orm.db.session.rollback()
            form.id.data = account.id

        return redirect(url_for('view_account'))
    elif request.method =='GET' and account_id:
        form = logic.GetAccountFormById(account_id)
        logic.LoadBasePageInfo('修改用户',form)
    else:
        logic.LoadBasePageInfo('新建用户',form)

    if form.id.data:
        account = orm.Account.query.get(int(form.id.data))
        form.account = account

    return render_template('view_account.html',form = form)



@app.route('/bd/view_accounts' , methods=['GET', 'POST'])
def view_accounts():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    pagination = orm.User.query.order_by(orm.User.id).paginate(page, 20)
    users = pagination.items

    if request.method == 'POST':
        form = AccountForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.User.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_accounts', page=page, q=q))

    form = PageInfo()
    logic.LoadBasePageInfo('所有用户',form)

    return render_template('view_accounts.html', form=form, pagination=pagination, users=users)


@app.route('/new/function', methods=['GET', 'POST'])
def new_funciton():
    return render_template('new_function.xml')
