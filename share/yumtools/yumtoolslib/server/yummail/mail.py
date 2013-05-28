# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText

def sendMail(sender, receiver, subject, text):
    email_body              = MIMEText(text, "plain", "UTF-8")
    email_body['Subject']   = u"%s" % subject
    email_body['From']      = sender
    email_body['To']        = receiver
    try:
        mail_sender = smtplib.SMTP()
        mail_sender.connect("mail.qunar.com")
        mail_sender.sendmail(sender, receiver, email_body.as_string())
        mail_sender.close()
        io.log('mail', "send mail succeed")
        return True
    except Exception, e:
        io.error('mail', "send mail succeed")
        return False

