from flask import Blueprint, redirect, url_for, render_template, current_app, flash
from flask_login import current_user, login_required
from . import mail_manager as mail
from .models import db
from .models.item import Item
from .models.store import Store
from .forms import ItemForm, DeleteForm, ContactForm
from .helper_role import HelperRole as hr

# Blueprint
main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

@main_bp.route('/')
def init():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.items_list'))
    else:
        return redirect(url_for("auth_bp.login"))

@main_bp.route('/contact', methods=["GET", "POST"])
@login_required
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = form.msg.data
        mail.send_contact_msg(current_user, msg)
        return redirect(url_for('main_bp.init'))
    
    return render_template('contact.html', form = form)

@main_bp.route('/items/list')
@login_required
@hr.require_view_permission.require(http_exception=403)
def items_list():
    # select on no cal fer join explícitament, tenint en compte la relació definida a models/store.py
    items = db.session.query(Item).order_by(Item.id.asc()).all()
    # depuració
    count = len(items)
    current_app.logger.info(f"Hi ha {count} items a la BD")
    # missatges flash
    flash(f"Hi ha {count} items disponibles", "info")
    # mostrar pàgina
    return render_template('items_list.html', items = items)

@main_bp.route('/items/update/<int:item_id>',methods = ['POST', 'GET'])
@login_required
@hr.require_edit_permission.require(http_exception=403)
def items_update(item_id):
    # select amb 1 resultat
    item = db.session.query(Item).filter(Item.id == item_id).one()

    # select que retorna una llista de resultats
    stores = db.session.query(Store).order_by(Store.id.asc()).all()
    
    # creo el formulari amb les dades de l'item
    form = ItemForm(obj = item)
    form.store_id.choices = [(store.id, store.nom) for store in stores]
    
    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # dades del formulari a l'objecte item
        form.populate_obj(item)

        # update!
        db.session.add(item)
        db.session.commit()

        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for('main_bp.items_read', item_id = item_id))
    else: #GET
        return render_template('items_update.html', item_id = item_id, form = form)

@main_bp.route('/items/create', methods = ['POST', 'GET'])
@login_required
@hr.require_edit_permission.require(http_exception=403)
def items_create(): 
    # select que retorna una llista de resultats
    stores = db.session.query(Store).order_by(Store.id.asc()).all()

    # creo el formulari buit
    form = ItemForm()
    form.store_id.choices = [(store.id, store.nom) for store in stores]

    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # he de crear un nou item
        new_item = Item()
        # dades del formulari a l'objecte item
        form.populate_obj(new_item)

        # insert!
        db.session.add(new_item)
        db.session.commit()

        # https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for('main_bp.items_list'))
    else: #GET
        return render_template('items_create.html', form = form)


@main_bp.route('/items/read/<int:item_id>')
@login_required
@hr.require_view_permission.require(http_exception=403)
def items_read(item_id):
    # select amb un resultat i sense join explícitament, tenint en compte la relació definida a models/store.py
    item = db.session.query(Item).filter(Item.id == item_id).one()
    
    return render_template('items_read.html', item = item)

@main_bp.route('/items/delete/<int:item_id>',methods = ['GET', 'POST'])
@login_required
@hr.require_edit_permission.require(http_exception=403)
def items_delete(item_id):
    # select amb 1 resultat
    item = db.session.query(Item).filter(Item.id == item_id).one()

    form = DeleteForm()
    if form.validate_on_submit(): # si s'ha fet submit al formulari
        # delete!
        db.session.delete(item)
        db.session.commit()

        return redirect(url_for('main_bp.items_list'))
    else: # GET
        return render_template('items_delete.html', item = item, form = form)
