#-*- coding: utf-8 -*-
import sys,os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../..'))


reload(sys)
sys.setdefaultencoding('utf-8')
from DB import orm
from forms import SchoolForm, InstitutionForm, BulletinForm, AccountForm
from Logic import restful

g_choices_area = [(g.id, g.name) for g in orm.Area.query.order_by('name')]
g_choices_schooltype = [(g.id, g.name) for g in orm.Schooltype.query.order_by('name')]
g_choices_feature = [(g.id, g.name) for g in orm.Feature.query.order_by('name')]
g_choices_agespan = [(g.id, g.name) for g in orm.Agespan.query.order_by('name')]
g_choices_feetype = [(g.id, g.name) for g in orm.Feetype.query.order_by('name')]


def GetSchoolFormById(school_id):
    school = orm.School.query.get(int(school_id))
    if school is None: return None
    schoolform = SchoolForm()
    schoolform.id.data = school.id
    schoolform.name.data = school.name
    schoolform.area_id.data = school.area_id
    schoolform.area_name = school.area.name
    schoolform.teachdesc.data = school.teachdesc
    schoolform.address.data = school.address
    schoolform.schooltype_id.data = school.schooltype_id
    schoolform.schooltype_name = school.schooltype.name
    schoolform.website.data = school.website
    schoolform.distinguish.data = school.distinguish
    schoolform.leisure.data = school.leisure
    schoolform.threashold.data =school.threashold
    schoolform.partner.data = school.partner
    schoolform.artsource.data = school.artsource
    schoolform.feedesc.data = school.feedesc
    schoolform.longitude.data =school.longitude
    schoolform.latitude.data = school.latitude
    schoolform.schoolimages = school.schoolimages
    schoolform.feature_ids.data = [x.feature_id for x in school.schoolfeatures]

    schoolform.area_id.choices = g_choices_area
    schoolform.schooltype_id.choices = g_choices_schooltype
    schoolform.feature_ids.choices = g_choices_feature
    return schoolform


def SetSchoolFeatures(school_id, feature_ids):
    for x in orm.SchoolFeature.query.filter_by(school_id=school_id).all():
        orm.db.session.delete(x)
    for x in feature_ids:
        sf = orm.SchoolFeature(school_id, x)
        orm.db.session.add(sf)
    orm.db.session.commit()


def SetInstitutionFeatures(institution_id, feature_ids):
    for x in orm.InstitutionFeature.query.filter_by(institution_id=institution_id).all():
        orm.db.session.delete(x)
    for x in feature_ids:
        sf = orm.InstitutionFeature(institution_id, x)
        orm.db.session.add(sf)
    orm.db.session.commit()


def GetInstitutionFormById(institution_id):
    institution = orm.Institution.query.get(int(institution_id))
    if institution is None: return None
    institutionform = InstitutionForm()
    institutionform.id.data = institution.id
    institutionform.name.data = institution.name
    institutionform.agespan_id.data = institution.agespan_id
    institutionform.agespan_name = institution.agespan.name
    institutionform.area_id.data = institution.area_id
    institutionform.area_name = institution.area.name
    institutionform.address.data = institution.address
    institutionform.location.data = institution.location
    institutionform.website.data = institution.website
    institutionform.telephone.data = institution.telephone
    institutionform.feedesc.data = institution.feedesc
    institutionform.timeopen.data =institution.timeopen
    institutionform.timeclose.data = institution.timeclose
    institutionform.feetype_id.data = institution.feetype_id
    institutionform.feetype_name = institution.feetype.name
    institutionform.longitude.data =institution.longitude
    institutionform.latitude.data = institution.latitude
    institutionform.institutionimages = institution.institutionimages
    institutionform.feature_ids.data = [x.feature_id for x in institution.institutionfeatures]

    institutionform.area_id.choices = g_choices_area
    institutionform.feature_ids.choices = g_choices_feature
    institutionform.agespan_id.choices =g_choices_agespan
    institutionform.feetype_id.choices = g_choices_feetype

    return institutionform


def GetBulletinFormById(bulletin_id):
    bulletin = orm.Bulletin.query.get(int(bulletin_id))
    if bulletin is None: return None
    bulletinform = BulletinForm()
    bulletinform.id.data = bulletin.id
    bulletinform.title.data = bulletin.title
    bulletinform.content.data = bulletin.content
    bulletinform.dt.data = bulletin.dt
    bulletinform.valid.data = bulletin.valid
    bulletinform.source.data = bulletin.source
    bulletinform.author.data = bulletin.author
    return bulletinform


def GetAccountFormById(account_id):
    account = orm.Account.query.get(int(account_id))
    if account is None: return None
    accountform = AccountForm()
    accountform.id.data = account.id
    accountform.username.data = account.username
    accountform.password.data = account.password
    accountform.name.data = account.name
    accountform.telephone.data = account.telephone
    accountform.flag_telephone.data = True if account.flag_telephone >0 else False
    accountform.checkcode.data = account.checkcode
    accountform.source.data = account.source
    accountform.dtcreate.data = account.dtcreate
    return accountform


def LoadBasePageInfo(pagename, pagetask, form):
    form.pagename = pagename;
    form.pagetask = pagetask;
    form.school_count = orm.School.query.count()
    form.institution_count = orm.Institution.query.count()
    form.bulletin_count = orm.Bulletin.query.count()
    form.account_count = orm.Account.query.count()


def SetDefaultImage(obj):
    if obj.has_key(restful.ITEM_BULLETINIMAGES):
        listimage = obj.get(restful.ITEM_BULLETINIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_bulletinimage.jpg'})

    if obj.has_key(restful.ITEM_INSTITUTIONIMAGES):
        listimage = obj.get(restful.ITEM_INSTITUTIONIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_institutionimage.jpg'})

    if obj.has_key(restful.ITEM_SCHOOLIMAGES):
        listimage = obj.get(restful.ITEM_SCHOOLIMAGES,[])
        if len(listimage)<=0:
            listimage.append({restful.ITEM_ID:0,restful.ITEM_FILE:'default_schoolimage.jpg'})

if __name__ == '__main__':
    print orm.Area.query.get(1)


