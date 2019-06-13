import smtplib

from main import Singleton


class Sender(metaclass=Singleton):
    """Sender factory. Instance is mail sending method. Special handling for GMail included :)"""
    def __init__(self, config_mail):
        self.config = config_mail
        if config_mail.smtp == 'smtp.gmail.com':
            self.service = self._send_mail_gmail
        else:
            self.service = self._send_mail_regular

    def _send_mail_gmail(self, message):
        """
        Send composed mail message through GMail
        :param msg: MIMEMultipart('alternative')
        :return: None if everything is ok, else exception message
        """
        server = smtplib.SMTP(self.config.smtp, self.config.smtp_port)
        try:
            server.ehlo()
            server.starttls()
            server.login(self.config.smtp_login, self.config.smtp_pass)
            server.send_message(message)
        except Exception as e:
            return e
        server.quit()
        return None

    def _send_mail_regular(self, message):
        """
        Send composed mail message through regular SSL secured SMTP server
        :param msg: MIMEMultipart('alternative')
        :return: None if everything is ok, else exception message
        """
        server = smtplib.SMTP_SSL(self.config.smtp, self.config.smtp_port)
        try:
            server.login(self.config.smtp_login, self.config.smtp_pass)
            server.send_message(message)
        except Exception as e:
            return e
        server.quit()
        return None
