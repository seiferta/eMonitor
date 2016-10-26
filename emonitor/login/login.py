from flask import Blueprint, request, current_app, render_template, flash, redirect, url_for
import flask_login
from flask_babel import gettext
from emonitor.decorators import login_required
from emonitor.user import User
from emonitor.extensions import db

login = Blueprint('login', __name__, template_folder="templates")

gettext(u'admin.login.needed')
gettext(u'admin.loginerror')
gettext(u'login.currpwdwrong')


@login.route("/login", methods=["GET", "POST"])
def loginform():
    """
    Create login form under url */login* with username and password field.

    :return: rendered template */emonitor/login/templates/login.html*
    """
    if request.method == "POST":
        user = User.getUserByName(request.form.get('username'))

        if user and user.check_password(request.form.get('password')):
            if request.form.get('remember', '') == '1':
                flask_login.login_user(user, remember=True)
            else:
                flask_login.login_user(user, remember=False)
            return redirect(request.form.get("next") or "/")
        else:
            flash('admin.loginerror', 'error')
    return render_template('login.html', next=request.args.get('next', ''), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))
    
    
# logout page
@login.route("/logout")
@login_required
def logout():
    """
    Register url */logout* to logout current user. Redirect to frontend base url */*
    """
    flask_login.logout_user()
    return redirect(url_for('frontend.frontendContent'))


# user page
@login.route("/user", methods=["GET", "POST"])
@login_required
def usersettings():
    """
    Register url */user* for user settings

    :return: rendered template */emonitor/login/templates/login_settings.html*
    """
    if request.method == "POST":
        user = User.getUsers(flask_login.current_user.get_id() or -1)
        if not user.check_password(request.form.get('curpwd')):
            flash('login.currpwdwrong')
        elif request.form.get('newpwd') != request.form.get('newpwdcheck'):
            flash('login.pwdnomatch')
        else:
            user._set_password(request.form.get('newpwdcheck'))
            db.session.commit()
            return redirect("/")

    return render_template('login_settings.html', user=User.getUsers(flask_login.current_user.get_id() or -1), app_name=current_app.config.get('PROJECT'), app_version=current_app.config.get('APP_VERSION'))
