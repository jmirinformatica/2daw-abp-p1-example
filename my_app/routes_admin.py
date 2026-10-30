from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models.user import User
from .helper_role import HelperRole as hr
from .models import db
from .forms import DeleteUsersForm

# Blueprint
admin_bp = Blueprint(
    "admin_bp", __name__, template_folder="templates/admin", static_folder="static"
)

@admin_bp.route('/admin')
@login_required
@hr.require_editor_role.require(http_exception=403)
def admin_index():
    return render_template('index.html')

@admin_bp.route('/admin/users')
@login_required
@hr.require_editor_role.require(http_exception=403)
def admin_users():
    users = User.query.all()
    form = DeleteUsersForm()
    return render_template('users_list.html', users=users, form=form)

@admin_bp.route('/admin/remove_users', methods=['POST'])
@login_required
@hr.require_editor_role.require(http_exception=403)
def remove_users():
    form = DeleteUsersForm()
    # Validem el formulari
    if form.validate_on_submit():
        user_ids = request.form.getlist('users')
        # Eliminem usuaris seleccionats
        if user_ids:
            User.query.filter(
                User.id.in_(user_ids)
            ).delete(synchronize_session=False)
            db.session.commit()
            flash(f'{len(user_ids)} usuaris eliminats.', 'success')
        else:
            flash('Selecciona almenys un/a usuari/a.', 'warning')
    else:
        flash('Error de validació del formulari.', 'danger')

    return redirect(url_for('admin_bp.admin_users'))