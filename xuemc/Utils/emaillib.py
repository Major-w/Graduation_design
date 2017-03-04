
#!/usr/bin/python
# emaillib.py

import smtplib
from email.mime.text import MIMEText

def SendEmail(email_title, email_content, listEmailAddress):

    mail_host="smtp.ym.163.com"
    mail_user="admin"
    mail_pass="HON123well"
    mail_postfix="honhome.com"

    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(email_content,'html','utf-8')
    msg['Subject'] = email_title
    msg['From'] = me
    msg['To'] = ";".join(listEmailAddress)
    try:
        s = smtplib.SMTP(mail_host)
#         s.starttls()
        s.login(mail_user+"@"+mail_postfix,mail_pass)
        s.sendmail(me, listEmailAddress, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    tolist =  ['changlong.liu@honeywell.com']
    content = 'Emergency, your house fired. Please call 119'
    title = 'fire alarm'

    if SendEmail(title, content, tolist):
        print 'sent out successfully'
    else:
        print 'sent fail'
