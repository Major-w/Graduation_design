#-*- coding: utf-8 -*-
import os
import time, uuid, datetime
from flask import render_template, send_from_directory, session, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask import Markup, request
from app import app, db
from forms import SchoolForm, PageInfo, InstitutionForm, BulletinForm, AccountForm, LoginForm, RegistrationForm,\
    PasswordResetRequestForm, PasswordResetForm
from DB import orm
from Utils import Util
from Logic import restful, logic
from .email import send_email
from models import User


@app.route('/bd/web/<path:path>')
def rootDir_web(path):
    index_key = path.rfind('py')
    if index_key > (len(path)-4):
        return redirect(url_for('view_schools'))
    return send_from_directory(os.path.join(app.root_path, '.'), path)


UPLOAD_PATH = '/home/lynn/project/bd/python/web/files/'


@app.route('/')
def rootDir():
    return redirect(url_for('login'))


@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('view_school'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('view_school'))
        if user.reset_password(token, form.password.data):
            flash(u'您的密码已经更新.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('view_school'))
    return render_template('auth/reset_password.html', form=form)


@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('view_school'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
        return redirect(url_for('view_school'))
    if current_user.confirm(token):
        flash(u'您已经激活了您的账户')
    else:
        flash(u'链接已失效')
    return redirect(url_for('view_school'))


@app.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'已经发送了一封邮件到您的邮箱中，请确认')
    return redirect(url_for('view_school'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('view_school'))
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
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
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


@app.route('/bd/view_school', methods=['GET', 'POST'])
def view_school():
    school_id = request.args.get('id')
    q = request.args.get('q')
    if q is not None:
        return redirect(url_for('view_schools', page=1, q=q))        
    form = SchoolForm(request.form)
    form.area_id.choices = logic.g_choices_area
    form.schooltype_id.choices = logic.g_choices_schooltype
    form.feature_ids.choices = logic.g_choices_feature
#    form.message = form.data
    if request.method == 'POST' and form.validate():
        print "longitude:",form.longitude.data
        if form.id.data:
            school = orm.School.query.get(int(form.id.data))
            school.name = form.name.data
            school.area_id = form.area_id.data
            school.teachdesc = form.teachdesc.data
            school.address = form.address.data
            school.schooltype_id = form.schooltype_id.data
            school.website = form.website.data
            school.distinguish = form.distinguish.data
            school.leisure = form.leisure.data
            school.threashold = form.threashold.data
            school.partner = form.partner.data
            school.artsource = form.artsource.data
            school.feedesc = form.feedesc.data
            school.longitude = form.longitude.data
            school.latitude = form.latitude.data
            orm.db.session.commit()
        else:
            school = orm.School(form.name.data, form.area_id.data, form.teachdesc.data, form.address.data, form.schooltype_id.data, form.website.data, form.distinguish.data, form.leisure.data, form.threashold.data, form.partner.data, form.artsource.data, form.feedesc.data, form.longitude.data, form.latitude.data)
            orm.db.session.add(school)
            orm.db.session.commit()
            form.id.data = school.id

        logic.SetSchoolFeatures(int(form.id.data),form.feature_ids.data)

        if request.form.has_key('upload'):
            file = request.files['image']
            if file :
                file_server = str(uuid.uuid1())+Util.file_extension(file.filename)
                pathfile_server = os.path.join(UPLOAD_PATH, file_server)
                file.save(pathfile_server)          
                if os.stat(pathfile_server).st_size <1*1024*1024:
                    schoolimage = orm.Schoolimage(school.id,file_server)
                    orm.db.session.merge(schoolimage)
                    orm.db.session.commit()
                else:
                    os.remove(pathfile_server)
        else:
            return redirect(url_for('view_school'))
    elif request.method =='GET' and school_id:
        form = logic.GetSchoolFormById(school_id)
        logic.LoadBasePageInfo('修改学校',form)
    else:
        logic.LoadBasePageInfo('新建学校',form)

    if form.id.data:
        school = orm.School.query.get(int(form.id.data))
        form.school = school
        if form.school:
            form.schoolimages = form.school.schoolimages
    
    return render_template('view_school.html',form = form)



@app.route('/bd/view_schools' , methods=['GET', 'POST'])
def view_schools():
    page = request.args.get('page', 1)
    q = request.args.get('q')
    schools = restful.GetSchools(int(page), q)
    if not schools.has_key(restful.ITEM_OBJECTS):
        return redirect(url_for('view_schools'))        

    schoolforms =[logic.GetSchoolFormById(x[restful.ITEM_ID]) for x in schools[restful.ITEM_OBJECTS]]
    while None in schoolforms:
        schoolforms.remove(None)
    

#    form.message = form.data
    if request.method == 'POST':
        form = SchoolForm(request.form)
        if request.form.has_key('delete'):
            for x in orm.Schoolimage.query.filter_by(school_id=int(form.id.data)).all():
                pathfile_server = os.path.join(UPLOAD_PATH, x.file)
                if os.path.exists(pathfile_server):
                    os.remove(pathfile_server)
            orm.db.session.delete(orm.School.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_schools', page=page, q=q))

    form = PageInfo()
    logic.LoadBasePageInfo('所有学校',form)
    
    return render_template('view_schools.html',forms = schoolforms,form = form, paging=restful.GetPagingFromResult(schools))



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
    logic.LoadBasePageInfo('所有培训机构',form)
    
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
                    orm.db.session.commit()
                else:
                    os.remove(pathfile_server)
        else:
            return redirect(url_for('view_bulletin'))
    elif request.method =='GET' and bulletin_id:
        form = logic.GetBulletinFormById(bulletin_id)
        logic.LoadBasePageInfo('修改公告',form)
    else:
        form.dt.data = datetime.datetime.now()
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
            orm.db.session.commit()
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
    page = request.args.get('page', 1)
    q = request.args.get('q')
    accounts = restful.GetAccounts(int(page),q)
    if not accounts.has_key(restful.ITEM_OBJECTS):
        return redirect(url_for('view_accounts'))        

    accountforms =[logic.GetAccountFormById(x[restful.ITEM_ID]) for x in accounts[restful.ITEM_OBJECTS]]
    while None in accountforms:
        accountforms.remove(None)

    if request.method == 'POST':
        form = AccountForm(request.form)
        if request.form.has_key('delete'):
            orm.db.session.delete(orm.Account.query.get(int(form.id.data)))
            orm.db.session.commit()
            return redirect(url_for('view_accounts', page=page, q=q))

    form = PageInfo()        
    logic.LoadBasePageInfo('所有用户',form)
    
    return render_template('view_accounts.html',forms = accountforms,form = form, paging=restful.GetPagingFromResult(accounts))

