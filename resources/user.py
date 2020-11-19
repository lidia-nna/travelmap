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
from models.images import ImagesModel
import os
import warnings
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


update_parser = reqparse.RequestParser()
update_parser.add_argument('email')

update_parser.add_argument('password')

update_parser.add_argument('username')


class UserHome(Resource):
    @jwt_required
    def get(self, user_id):
        api_key = os.environ.get('GM_API_KEY')
        return make_response(render_template('home.html', user_id=user_id, key=api_key), 200, {'Content-Type': 'text/html'})


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
        self.confirm_email(
            email=data.email,
            subject="Travelmap account registration",
            template="email_template.html"
        )
        user = UserModel(email=data.email)
        user.set_password(data.password)
        user.set_username()

        try:
            user.save_to_db()
            flash('A confirmation email has been sent via email.', 'success')
            return redirect('/register')
        except Exception as e:
            return {'message': f'Something went wrong: {e}'}, 400
    

    def confirm_email(self, email, subject, template):
        token = Token()
        mytoken = token.generate_confirmation_token(email=email)
        confemail = Email()
        #url = url_for("confirmregistration", token=mytoken)
        url= f'http://127.0.0.1:5000/confirmreg/{mytoken}'
        confemail.send_email(
            subject=subject, 
            to=email, 
            template=render_template(template, confirm_url=url))



    # def retrieve_user_data(self):
    #     user_id = get_jwt_identity()
    #     user = UserModel.find_user(user_id)
    #     new_user = UserModel(
    #         id = user.id,
    #         email = user.email,
    #         password_hash = user.password_hash,
    #         confirmed = user.confirmed,
    #         confirmed_on = user.confirmed_on,
    #         registered_on = user.registared_on,
    #         user = user.username
    #     )
    #     return new_user

     # update password/email/username
    #@jwt_required     
    def put(self):
        request_args = update_parser.parse_args()
        # username = get_jwt_identity()
        username = 'Anna'
        try:
            UserModel.update_to_db(username, **request_args)
            if request_args.email:
                send_confirmation = {
                    'email' : request_args.email, 
                    'subject' : "Travelmap email update confirmation",
                    'template' : "email_template_2.html"
                }
                self.confirm_email(**send_confirmation)
        except Exception as e:
            return {"message": str(e)}
        return "Update successful"
 

    #remove the profile
    def delete(self):
        #username = get_jwt_identity()
        username = "lid.mijas"
        user = UserModel.find_user(username)
        print(user.id)
        images= ImagesModel.find_by_user(user.id)
        if images:
            record = images[0]
            image_dir = os.path.abspath(os.path.dirname(record.filepath))
        try:
            user.delete()
        except Exception as e:
            print('Failed to remove the user record' +str(e))
            return "Removal unsuccessful"
        else:
            # for image in images:
            #     try:
            #         ImagesModel.delete_files(image)
            #     except OSError as e:
            #         warnings.warn("Couldn't remove the image, image does not exist:" + str(e)) 
            #     except IOError as e:
            #          warnings.warn('No permissions to remove the image:'+str(e))
            #     else:
            #         print(f'Image {image} removed')

            try:
                os.remove(image_dir)
            except Exception as e:
                warnings.warn('data not removed:' + str(e))
                return "Removal partially successful"
            else:
                filepaths = (image.filepath for image in images)
                is_data_removed = (os.path.exists(filepath) for filepath in filepaths)
                if sum(is_data_removed) > 0:
                    return "Removal partially successful"
        return "Removal successful"
        

    

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