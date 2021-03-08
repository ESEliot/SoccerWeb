# List of imports
import copy
import csv
import bcrypt
from django.core import mail
from flask import Flask, render_template, redirect, flash, session, request
from flask_login import UserMixin, LoginManager, login_user
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Email, Length, EqualTo
from wtforms.fields.html5 import EmailField
from wtforms import StringField, TextAreaField, PasswordField, form, DateTimeField, FileField, IntegerField
from flask_mail import Message, Mail

app = Flask(__name__)

# Loging in manager and session creation

login_manage = LoginManager()
app.secret_key = 'bobby'
login_manage.init_app(app)
login_manage.login_view = 'login'
app.config['USE_SESSION_FOR_NEXT'] = True


# Base template (inherited by all other templates)
@app.route('/base_template.html')
def base():
    return render_template('base_template.html', username=session.get('username'), name=session.get('name'))


# Homepage
@app.route('/')
def homepage():
    return render_template('homepage_template.html', username=session.get('username'), name=session.get('name'))


# Homepage when clicked will go back to homepage
@app.route('/littleStar')
def littleStar():
    return render_template('littleStar.html', username=session.get('username'), name=session.get('name'))


# Champions league information
@app.route('/champions')
def champions():
    return render_template('champions_template.html', username=session.get('username'), name=session.get('name'))


# Activities page
@app.route('/activities')
def activities():
    return render_template('activities.html', username=session.get('username'), name=session.get('name'))


# About Us
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', username=session.get('username'), name=session.get('name'))


# Match maker
@app.route('/matchMake')
def matchMake():
    return render_template("matchMake.html", username=session.get('username'), name=session.get('name'))


# Login
@app.route('/login')
def login_template():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = find_user(form.username.data)

        if user and bcrypt.checkpw(form.password.data.encode(),
                                   user.password.encode()):
            login_user(user)
            flash('Logged in successfully.')
            next_page = session.get('next', '/')
            session['next'] = '/'
            print(user.name)
            print(form.username.data)
            session['name'] = user.name
            session['username'] = form.username.data
            print('Log in good')
            return redirect(next_page)
        else:
            flash('Incorrect username/password.')
    return render_template('login_template.html', form=form, name=session.get('name'), username=session.get('username'))


@app.route('/registrationform')
def register_template():
    form = RegisterForm()
    return render_template("register_template.html", username=session.get('username'), name=session.get('name'),
                           form=form)


# Users Table route - Users Table page (Only accessible for Admin)
@app.route('/userstable')
def userstable_template():
    with open('../../PycharmProjects/SOEN287_A3_40021696_ELIESABBAGH/data/users.csv') as f:
        users_list = list(csv.reader(f))[1:]
    return render_template("users_template.html", form=form, name=session.get('name'), username=session.get('username'),
                           users_list=users_list)


# USER ----------------------------------------------------------------------------------------------------
# User class
class User(UserMixin):
    def __init__(self, username, email, name, password=None):
        self.email = email
        self.name = name
        self.id = username
        self.password = password


# Registration

# RegisterForm - Form for registration - Atrributes of the form: name, username, email, password, password2
class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    name = StringField('Name', validators=[InputRequired()])

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(),
                                                     Length(8)])
    password2 = PasswordField('Repeat password',
                              validators=[InputRequired(),
                                          EqualTo('password', message='Passwords must match.')])


# CSV file to record users history
def find_user(username):
    with open('../../PycharmProjects/SOEN287_A3_40021696_ELIESABBAGH/data/users.csv', 'r') as f:
        for user in csv.reader(f):
            if username == user[0]:
                return User(*user)
    return None


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form1 = RegisterForm(request.form)
    print(form1.errors)
    if form1.validate_on_submit():
        finduser = find_user(form1.username.data)
        if finduser:
            flash('This username already exists. Choose another one please')
            return render_template('register_template.html', form=form1)
        if not finduser:
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(form1.password.data.encode(),
                                     salt)
            with open('../../PycharmProjects/SOEN287_A3_40021696_ELIESABBAGH/data/users.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([form1.username.data,
                                 form1.email.data,
                                 form1.name.data,
                                 password.decode()])
                flash('Registered successfully.')
        session['name'] = form1.name.data
        return render_template('register_response.html', form=form1, name=session.get('name'))

    message = copy.deepcopy(form1.errors)
    return render_template('register_template.html', form=form1, message=message)


# END REGISTRATION ----------------------------------------------------------------------------------------------------


# LOGIN ------------------------------------------------------------------------------------------------------------
# Login Manager that returns user
@login_manage.user_loader
def load_user(user_id):
    user = find_user(user_id)

    if user:

        user.password = None
    return user


# Login form: username and password
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


# Handleogin route
@app.route('/handlelogin', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = find_user(form.username.data)
        # user could be None
        # passwords are kept in hashed form, using the bcrypt algorithm
        if user and bcrypt.checkpw(form.password.data.encode(),
                                   user.password.encode()):
            login_user(user)
            flash('Logged in successfully.')
            next_page = session.get('next', '/')
            session['next'] = '/'
            print(user.name)
            print(form.username.data)
            session['name'] = user.name
            session['username'] = form.username.data
            print('Log in good')
            return redirect(next_page)
        else:
            flash('Incorrect username/password.')
    return render_template('login_template.html', form=form, name=session.get('name'), username=session.get('username'))


# ENDLOGIN ------------------------------------------------------------------------------------------------------------

# LOGOUT ------------------------------------------------------------------------------------------------------------
# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return render_template('littleStar.html')


# END LOGOUT ----------------------------------------------------------------------------------------------------------


# CREATE PROJECT ------------------------------------------------------------------------------------------------------
# Project class
class Project(FlaskForm):
    matchChoices = [('o1', 'Goalkeeper'), ('o2', 'Center Back'), ('o3', 'Striker'), ('o4', 'Attacking Midfielder'),
                    ('o5', 'Box-to-Box Midfielder'), ('o6', 'Holding Midfielder')]
    name = StringField('Name', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    file = FileField('Upload any useful file here for the community:', validators=[InputRequired()])


# Create Project route
@app.route('/createproject', methods=['GET', 'POST'])
def createproject_template():
    form = Project(request.form)
    print(form.errors)
    if form.validate_on_submit():
        with open('../../PycharmProjects/SOEN287_A3_40021696_ELIESABBAGH/data/match.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([form.name.data,
                             form.matchChoices,
                             form.description.data,
                             form.file.data])
            flash('Project Submitted!')
        return render_template("createproject_response_template.html", form=form, name=session.get('name'),
                               username=session.get('username'))
    return render_template("createproject_template.html", form=form)


# END CREATE PROJECT --------------------------------------------------------------------------------------------------

# FORGOT PASSWORD ------------------------------------------------------------------------------------------------------
# Forgot form
class ForgotForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])


# Reset Password Form
class PasswordResetForm(FlaskForm):
    current_password = PasswordField('Password', validators=[InputRequired(),
                                                             Length(8)])


# Forgot Password route
@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword_template():
    form = ForgotForm(request.form)
    if form.validate_on_submit():
        msg = Message('Reset your password with the link below: ', sender='littlestarsoen287@gmail.com',
                      recipients=[form.email.data])
        mail.send(msg)
        return render_template('forgotPassword_sent.html', name=session.get('name'), username=session.get('username'),
                               form=form)
    return render_template("forgotPassword_template.html", name=session.get('name'), username=session.get('username'),
                           form=form)


# END FORGOT PASSWORD -------------------------------------------------------------------------------------------------

# MAIL ------------------------------------------------------------------------------------------------------------
# Mail configuration
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='littlestarsoen287@gmail.com',
    MAIL_PASSWORD='F00tb@ll',

))
mail = Mail(app)


# END MAIL --------------------------------------------------------------------------------------------------------


# Reservation ---------------------------------------------------------------------------------------------------------
# Reservation form
class ReservationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    time = IntegerField('Time', validators=[InputRequired()])
    people = IntegerField('People', validators=[InputRequired()])


@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    form1 = ReservationForm(request.form)
    if form1.validate_on_submit():
        print('hello zbi')
        return render_template('reservation_response.html', name=session.get('name'), username=session.get('username'),
                               form=form1)
    print('bye')
    return render_template('reservation.html', username=session.get('username'), name=session.get('name'), form=form1)


if __name__ == "__main__":
    app.secret_key = "bobby"
    app.run()