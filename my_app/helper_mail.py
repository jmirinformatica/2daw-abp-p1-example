import smtplib, ssl
from email.message import EmailMessage
from email.utils import formataddr

class MailManager:

    def init_app(self, app):
        # agafo els paràmetres de configuració
        self.sender_name = app.config.get('MAIL_SENDER_NAME')
        self.sender_addr = app.config.get('MAIL_SENDER_ADDR')
        self.sender_password = app.config.get('MAIL_SENDER_PASSWORD')
        self.smtp_server = app.config.get('MAIL_SMTP_SERVER')
        self.smtp_port = app.config.get('MAIL_SMTP_PORT')
 
        # els missatges de contacte s'envien a aquesta adreça
        self.contact_addr = app.config.get('CONTACT_ADDR')

    # https://realpython.com/python-send-email/#option-2-using-starttls
    def send_contact_msg(self, user, msg):

        subject = "Missatge de contacte"
        content = f"""Missatge de contacte rebut de {user.email}:
        
        {msg}

        Salut!        
        """

        self.__send_mail(
            dst_name = "Receptor/a de contacte",
            dst_addr = self.contact_addr,
            subject = subject,
            content = content
        )

    # https://realpython.com/python-send-email/#option-2-using-starttls
    def __send_mail(self, dst_name, dst_addr, subject, content):
        context = ssl.create_default_context()
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.ehlo()  # Can be omitted
            # server.starttls(context=context)
            # TODO: set as parameter if TLS is enabled or not
            server.ehlo()  # Can be omitted
            #server.login(self.sender_addr, self.sender_password)
            # TODO: set as parameter if auth is enabled or not

            msg = EmailMessage()
            msg['From'] = formataddr((self.sender_name, self.sender_addr))
            msg['To'] = formataddr((dst_name, dst_addr))
            msg['Subject'] = subject
            msg.set_content(content)

            server.send_message(msg, from_addr=self.sender_addr, to_addrs=dst_addr)