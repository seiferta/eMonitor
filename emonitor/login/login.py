from flask import Blueprint, request, current_app, render_template, flash, redirect, url_for
from flask.ext import login as flasklogin
from flask.ext.babel import gettext
from emonitor.decorators import login_required
from emonitor.user import User
from emonitor.extensions import db

login = Blueprint('login', __name__, template_folder="templates")

gettext(u'admin.login.needed')


@login.route("/login", methods=["GET", "POST"])
def loginform():
    if request.method == "POST":
        user = User.getUserByName(request.form.get('username'))

        if user and user.check_password(request.form.get('password')):
            if request.form.get('remember', '') == '1':
                flasklogin.login_user(user, remember=True)
            else:
                flasklogin.login_user(user, remember=False)
            return redirect(request.form.get("next") or "/")
        else:
            flash('admin.loginerror', 'error')
    return render_template('login.html', next=request.args.get('next', ''), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))
    
    
# logout page
@login.route("/logout")
@login_required
def logout():
    flasklogin.logout_user()
    return redirect(url_for('frontend.frontendContent'))


# user page
@login.route("/user", methods=["GET", "POST"])
@login_required
def usersettings():
    if request.method == "POST":
        user = User.getUsers(flasklogin.current_user.get_id() or -1)
        if not user.check_password(request.form.get('curpwd')):
            flash('login.currpwdwrong')
        elif request.form.get('newpwd') != request.form.get('newpwdcheck'):
            flash('login.pwdnomatch')
        else:
            user._set_password(request.form.get('newpwdcheck'))
            db.session.commit()
            return redirect("/")

    return render_template('login_settings.html', user=User.getUsers(flasklogin.current_user.get_id() or -1), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))
