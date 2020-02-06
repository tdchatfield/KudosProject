import smtplib
from email.message import EmailMessage
import email
import configfile as conf


def alert_failed_award(sender_addr):
    msg = EmailMessage()
    msg['To'] = sender_addr
    msg['From'] = conf.MY_ACCOUNT
    msg['Subject'] = 'Award Rejected: You must enter a subject line in order to award Kudos!'
    body = 'Please check recent kudos awards you have made; those which were awarded without subject lines have been rejected!'
    msg.set_content(body)

    server_addr = 'smtp.office365.com'

    with smtplib.SMTP(server_addr, 587) as s:
        s.ehlo()
        s.starttls()
        s.login(conf.MY_ACCOUNT, conf.MY_PASS)
        s.sendmail(conf.MY_ACCOUNT, sender_addr, msg.as_string())

