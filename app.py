from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = "bluebell3310's flask website"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@localhost:3306/{}'.format(os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_Name'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 減少記憶體使用
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Flaskyyy]'
app.config['MAIL_SENDER'] = 'Flaskyyy Admin <flaskyyy@gmail.com>'
app.config['MAIL_ADMIN'] = os.environ.get('FLASKYYY_ADMIN')

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

mail = Mail(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
    
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/name_form', methods=['GET', 'POST'])
def name_form():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            if app.config['MAIL_ADMIN']:
                send_email(app.config['MAIL_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('name_form'))
    return render_template("name_form.html", form=form, name=session.get('name'), known=session.get('known', False))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<User %r>' % self.username

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender = app.config['MAIL_SENDER'], recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)