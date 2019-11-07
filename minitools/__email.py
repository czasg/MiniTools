from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP

__all__ = 'Emailer',


class Emailer:
    def __init__(self, server, account, password, receiver=None, **kwargs):
        self.server = SMTP(server, **kwargs)
        self.server.login(account, password)
        self.account = account
        self.receiver = receiver \
            if isinstance(receiver, list) \
            else [receiver] if receiver \
            else []

    def __del__(self):
        self.server.quit()

    def set_receiver(self, *args):
        self.receiver.extend(args)

    def send(self, subject, message, receiver=None, html=False):
        msg = MIMEText(message, 'html' if html else 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.account
        msg['To'] = ""
        recv = receiver or self.receiver
        assert recv, "You Must Configure Who to receive this email!"
        self.server.sendmail(self.account, recv, msg.as_string())
