from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from mail import mail
from flask import render_template

class Token:
    def __init__(self):
        self.config = {}
        with open("yourconfig.cfg", "r") as f:
            lines = [line.rstrip() for line in f]
            config_lines = [tuple(line.split("=")) for line in lines]
            self.config.update( {k:v for (k,v) in config_lines})


    def generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(self.config['SECRET_KEY'])
        return serializer.dumps(email, salt=self.config['SECURITY_PASSWORD_SALT'])


    def confirm_token(self, token, expiration=3600):
        serializer = URLSafeTimedSerializer(self.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=self.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except:
            return False
        else:
            return email

class Email(Token):
    def __init__(self):
        super().__init__()


    def send_email(self, to, subject, template):
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=self.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)


if __name__ == "__main__":
    from app import app
    mail.init_app(app)
    app.run(port=5500)
    token = Token()
    # print(token.config)
    mytoken = token.generate_confirmation_token('lid.mijas@gmail.com')
    # print(mytoken)

    email = Email()
    print(email.config)
    confirm_url= f'http://127.0.0.1:5500/confirmreg/{mytoken}'
    print(confirm_url)
    email.send_email(subject="Travelmap account registration", to='lid.mijas@gmail.com', template=render_template("email_template.html", confirm_url=confirm_url))