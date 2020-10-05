from flask import make_response, render_template, redirect, flash
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token,
    set_refresh_cookies, set_access_cookies, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, unset_jwt_cookies)
from models.user import UserModel
from flask.json import jsonify

import smtplib, datetime
from email.message import EmailMessage
from pathlib import Path
from string import Template
from emailtoken import Token, Email
from flask.helpers import url_for
parser = reqparse.RequestParser()
parser.add_argument(
    'email',
    help='This field cannot be blank',
    required=True
)

parser.add_argument(
    'password',
    help='This field cannot be blank',
    required=True
)

emailparser = reqparse.RequestParser()
emailparser.add_argument(
    'email',
    help='This field cannot be blank',
    required=True
)


class UserHome(Resource):
    @jwt_required
    def get(self, user_id):
        return make_response(render_template('home.html', user_id=user_id), 200, {'Content-Type': 'text/html'})


class UserLogin(Resource):
    #static
    def get(self):
        return make_response(render_template('index.html'), 200)

    def post(self):
        data = parser.parse_args()
        current_user = UserModel.check_user(email=data.email)
        if not current_user:
            flash(f'User {data.email} has not been found, please register below.', "danger")
            return redirect('/register')
        if not UserModel.is_password(current_user.passwd_hash, data.password):
            flash('Wrong credentials.', "danger")
            return redirect('/signin')
        if not current_user.confirmed:
            flash("You have not confirmed your account. Please check your inbox (and your spam folder) - you should have received an email with a confirmation link, otherwise resend the email.", "danger")
            return redirect('/unconfirmed')
        access_token = create_access_token(identity=current_user.username)
        refresh_token = create_refresh_token(identity=current_user.username)
        # resp = jsonify({'current_user': current_user.id})
        # resp = make_response(redirect(f'/home/{current_user.id}'))
        resp = make_response(redirect(url_for('userhome', user_id=current_user.id)))
        set_refresh_cookies(resp, refresh_token)
        set_access_cookies(resp, access_token)
        return resp
    
class UserRegistration(Resource):
    # render registration page
    def get(self):
        return make_response(render_template('register.html'), 200)

    def post(self):
        data = parser.parse_args()
        user = UserModel.check_user(email=data.email) 
        if user and user.confirmed:
            flash("You have already registered, please log in!", "warning")
            return redirect('/signin')
        elif user and not user.confirmed:
            flash("You have not confirmed your account. Please check your inbox (and your spam folder) - you should have received an email with a confirmation link, otherwise resend the email.")
            return redirect('/unconfirmed')
        # if UserModel.check_user(username=data.username):
        #     return {'message': 'this username already exists, please select a different name'}

        token = Token()
        mytoken = token.generate_confirmation_token(email=data.email)
        # email = EmailMessage()
        # email['from'] = 'Travelmap'
        # email['to'] = data.email
        # email['subject'] = "Travelmap account registration"
        # email.set_content(f"Thank you for registaring with travelmap. Please confirm your details by clicking in the below link:\n http://127.0.0.1:5500/confirmreg/{mytoken}")
        # with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        #     smtp.ehlo()
        #     smtp.starttls()
        #     smtp.login('play.python.test@gmail.com', 'Test123#')
        #     smtp.send_message(email)
        #     print('Sent!')

        confemail = Email()
        confirm_url= f'http://127.0.0.1:5000/confirmreg/{mytoken}'
        confemail.send_email(
            subject="Travelmap account registration", 
            to=data.email, 
            template=render_template("email_template.html", confirm_url=confirm_url))

        user = UserModel(email=data.email)
        user.set_password(data.password)
        user.set_username()

        try:
            user.save_to_db()
            # access_token = create_access_token(identity=user.username)
            # refresh_token = create_refresh_token(identity=user.username)
            flash('A confirmation email has been sent via email.', 'success')
            # set_refresh_cookies(resp, refresh_token)
            # set_access_cookies(resp, access_token)
            return redirect('/register')
        except Exception as e:
            return {'message': f'Something went wrong: {e}'}, 400

     # update password or email       
    def put(self):
        pass

    #remove the profile
    def delete(self):
        pass
class UnconfirmedRegistration(Resource):
    def get(self):
        return make_response(render_template('unconfirmed.html'), 200)
    def post(self):
        data = emailparser.parse_args()
        user = UserModel.check_user(email=data.email) 
        if user and not user.confirmed:
            token = Token()
            mytoken = token.generate_confirmation_token(user.email)
            confemail = Email()
            confirm_url= f'http://127.0.0.1:5000/confirmreg/{mytoken}'
            confemail.send_email(
                subject="Travelmap account registration", 
                to=data.email, 
                template=render_template("email_template.html", confirm_url=confirm_url)
                )
            flash('A confirmation email has been sent via email.', 'success')
            return redirect('/signin')
        flash("No account found, please ensure correct details or create a new account.", "warning")
        return redirect('/unconfirmed')
            

class ConfirmRegistration(Resource):
    def get(self, token):
        try:
            tokenclass = Token()
            email = tokenclass.confirm_token(token)
        except:
            flash('The confirmation link is invalid or has expired.', 'danger')
            return redirect('/register')
        else:
            user = UserModel.check_user(email=email)    
            if not user.confirmed:
                user.confirmed = True
                user.confirmed_on = datetime.datetime.now()
                user.save_to_db()
                flash('You have confirmed your account. Thanks!', 'success')
                return redirect('/signin')
            flash('Account already confirmed. Please login.', 'success')
            return redirect('/signin')


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        resp = jsonify({'current user': current_user})
        set_access_cookies(resp, access_token)
        return resp


class TokenRemove(Resource):
    def get(self):
        resp = make_response(redirect('/signin'))
        unset_jwt_cookies(resp)
        resp.set_cookie('refresh_token_cookie', expires=0)
        resp.set_cookie('csrf_refresh_token', expires=0)
        return resp

#to_test
class AllUsers(Resource): 
    def get(self):
        def to_json(x):
            return {
                'username': x.username,
                'email': x.email,
                'password': x.passwd_hash
            }
        return [to_json(user) for user in UserModel.query.all()]

    def delete(self):
        return UserModel.delete_all()

#to_test
class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42,
            'current user': get_jwt_identity()
        }