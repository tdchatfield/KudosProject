import smtplib
from datetime import datetime
import email
import configfile as conf
from email.message import EmailMessage
import pymysql

class NewsLetter(object):
    """Represents a newsletter to send to
    employees in the system"""
    def __init__(self, title, content, recipient_addrs=None):
        self.recipient_addrs = []
        self.title = title
        self.content = content
        self.is_html = False
        self.is_published = False
        if recipient_addrs is not None:
            self.recipient_addrs.extend(recipient_addrs)

    def send(self):
        try:
            with smtplib.SMTP(conf.SMTP_HOST, 587) as s:
                s.ehlo()
                s.starttls()
                s.login(conf.MY_ACCOUNT, conf.MY_PASS)

                for addr in set(self.recipient_addrs):
                    msg = EmailMessage()
                    msg['To'] = addr
                    msg['Subject'] = self.title.replace('\n', '')
                    msg.subject = self.title
                    msg.set_content(self.content)
                    try:
                        s.sendmail(conf.MY_ACCOUNT, addr, msg.as_string())

                    except:
                        with open('./tmp/' + 'test' + '.msg', 'wb') as email:
                            email.write(msg.as_bytes())            
            self.is_published = True
                    
        except Exception as e:
            print(e)

    def save(self):
        try:
            dbconn = pymysql.connect(
                conf.DB_HOST, conf.DB_USER, conf.DB_PASSWORD, conf.DB_SCHEMA
            )
            self.send()
            fields = (
                self.title.encode('ascii', 'ignore'),
                self.content,
                self.is_html,
                self.is_published
            )

            cursor = dbconn.cursor()
            cursor.execute(
                '''INSERT INTO kudos_newsletter
                (title, content, is_html, is_published)
                VALUES(%s, %s, %s, %s)
                ''',
                fields
            )
            dbconn.commit()

        except Exception as e:
            print(e)

def test_newsletter():
    test_newsletter = NewsLetter(
        title='testing newsletter functionality! 👍👍',
        content='some content here',
        recipient_addrs=['TC01@keyintelligence.uk']
    )
    test_newsletter.save()

if __name__ == "__main__":
    print('script running')
    test_newsletter()
    print('script finished running')

