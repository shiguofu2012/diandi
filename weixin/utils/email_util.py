# coding=utf-8

import smtplib


class Email(object):

    def __init__(self, sender, sender_passwd, host, port=25):
        self.mail_host = host
        self.mail_port = port
        self.sender = sender
        self.sender_password = sender_passwd
        self.init()

    def init(self):
        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(self.mai_host, self.mail_port)
        smtp_obj.login(self.sender, self.sender_passwd)

    def send_email(self, receivers, mail_data):
        pass
