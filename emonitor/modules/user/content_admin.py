from flask import request, render_template, current_app
from emonitor.extensions import db
from emonitor.user import User


def getAdminContent(self, **params):

    if request.method == 'POST':
        if request.form.get('action').startswith('edituser_'):
            actionuser = User.getUsers(int(request.form.get('action').split('_')[-1]))
            params.update({'actionuser': actionuser, 'userlevels': [(0, 'userlevel.notset'), (1, 'userlevel.admin'), (2, 'userlevel.user')]})
            return render_template('admin.user_actions.html', **params)

        elif request.form.get('action') == 'createuser':  # add new user
            params.update({'actionuser': User('', '', '', 2, '', active=False), 'userlevels': [(0, 'userlevel.notset'), (1, 'userlevel.admin'), (2, 'userlevel.user')]})
            return render_template('admin.user_actions.html', **params)

        elif request.form.get('action').startswith('deleteuser_'):  # delet user
            db.session.delete(User.getUsers(request.form.get('action').split('_')[-1]))
            db.session.commit()

        elif request.form.get('action') == 'updateuser':  # update user
            if request.form.get('user_id') == 'None':  # add new user
                actionuser = User(request.form.get('edit_username'), current_app.config.get('DEFAULTPASSWORD', 'ABC'), '', 2, '', active=False)
                db.session.add(actionuser)
            else:
                actionuser = User.getUsers(int(request.form.get('user_id')))
            actionuser.email = request.form.get('edit_email')
            actionuser.level = request.form.get('edit_level')
            actionuser.active = request.form.get('edit_active', '0') == '1'
            db.session.commit()

    params.update({'users': User.getUsers(), 'userlevels': [(0, 'userlevel.notset'), (1, 'userlevel.admin'), (2, 'userlevel.user')]})
    return render_template('admin.user.html', **params)