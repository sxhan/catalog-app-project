from __future__ import absolute_import

import logging
from functools import wraps

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, abort
from flask_login import login_user, login_required, logout_user

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from . import app, models, auth


# Connect to Database and create database session
engine = create_engine(app.config["DB_STRING"])
models.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def catch_exceptions(f):
    """Useful decorator for debugging
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            logging.error("Unhandled Error on %s" % f.__name__,
                          exc_info=True)
            return abort(500)
    return wrapper


def get_ordered_categories():
    categories = db_session.query(models.Category) \
                           .order_by(asc(models.Category.name))
    return categories


#############
#
# Main Route
#
#############

@app.route('/')
@app.route('/catalog/')
def index():
    print session
    categories = db_session.query(models.Category) \
                           .order_by(asc(models.Category.name))
    items = db_session.query(models.Item) \
                      .order_by(desc(models.Item.updated_date))
    return render_template('index.html',
                           categories=categories,
                           items=items)


##################
#
# Category Routes
#
##################

@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def NewCategory():
    # if 'username' not in login_session:
    #     return redirect('/login')
    if request.method == 'POST':
        new = models.Category(name=request.form['name'])
        db_session.add(new)
        # flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        db_session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newCategory.html')


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def ShowCategory(category_name):
    # Get category
    try:
        category = db_session.query(models.Category) \
                             .filter_by(name=category_name).one()
        items = db_session.query(models.Item).join(models.Category) \
                          .filter(models.Category.name == category_name).all()
    except NoResultFound:
        return abort(404)
    except Exception:
        logging.error("", exc_info=True)
        return abort(500)

    return render_template('showCategory.html',
                           items=items,
                           category=category,
                           categories=get_ordered_categories())


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def ShowItem(category_name, item_name):
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())
    except NoResultFound:
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)
    return render_template("showItem.html",
                           category=category,
                           item=item)


@app.route('/catalog/<string:category_name>/<string:item_name>/edit/',
           methods=['GET', 'POST'])
@login_required
def EditItem(category_name, item_name):

    # Get Item
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())
    except NoResultFound:
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)

    if request.method == 'POST':
        # Check 1: Ensure that all fields are passed back and has value
        # "If not all required fields are passed back or not all fields are "
        # "filled"
        if not all([field in request.form and request.form[field]
                    for field in ("name", "description")]):
            flash("Error: All fields are required!")
            return render_template(
                "editItem.html",
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                category=category)

        # Check 2: for duplicate item
        existing = db_session.query(models.Item) \
                             .filter_by(name=request.form["name"],
                                        category_id=category.id).all()

        # If user is entering duplicate item, stop this transaction
        if existing:
            flash("Error: Item with duplicate name/category combination "
                  "found.")
            return render_template(
                "editItem.html",
                name=request.form.get("name", ""),
                description=request.form.get("description", ""))

        # Edit item
        item.name = request.form["name"]
        item.description = request.form["description"]

        db_session.add(item)
        db_session.commit()
        flash("Edit Successful!")
        return redirect(url_for("ShowCategory",
                                category_name=category.name))

    else:
        return render_template("editItem.html",
                               name=item.name,
                               description=item.description,
                               category=category)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete/',
           methods=["GET", "POST"])
@login_required
def DeleteItem(category_name, item_name):
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())

        # Only owner can perform this action
        # FIXME change hard coded item value
        if item.user.id != 1:
            return abort(403)
    except NoResultFound:
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)

    if request.method == 'POST':
        if 'confirm' in request.form and request.form["confirm"] == "true":
            item_name = item.name  # Save the name for use later
            db_session.delete(item)
            db_session.commit()
            flash('Deleted %s' % item_name)
            return redirect(url_for('ShowCategory',
                                    category_name=category_name))
    else:
        return render_template('deleteItem.html',
                               category=category,
                               name=item.name)


@app.route('/catalog/item/new/', methods=['GET', 'POST'])
@catch_exceptions
@login_required
def NewItem():
    # This will be useful later
    categories = get_ordered_categories()

    if request.method == 'POST':
        # Check 1: Ensure that all fields are passed back and has value
        # "If not all required fields are passed back or not all fields are "
        # "filled"
        if not all([field in request.form and request.form[field]
                    for field in ("name", "description", "category")]):
            flash("Error: All fields are required!")
            return render_template(
                "newItem.html",
                categories=categories,
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                category=request.form.get("category", ""))

        # Attempt to create new item
        category = db_session.query(models.Category) \
                             .filter_by(name=request.form["category"]) \
                             .one()
        existing = db_session.query(models.Item) \
                             .filter_by(name=request.form["name"],
                                        category_id=category.id).all()

        # If user is entering duplicate item, stop this transaction
        if existing:
            flash("Error: Item with duplicate name/category combination "
                  "found.")
            return render_template(
                "newItem.html",
                categories=categories,
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                category=request.form.get("category", ""))

        # Continue with item creation
        item = models.Item(name=request.form["name"],
                           description=request.form["description"],
                           category_id=category.id,
                           user_id=1)
        # FIXME change user once user is implemented
        db_session.add(item)
        db_session.commit()
        return redirect(url_for("ShowCategory",
                        category_name=category.name))

    else:
        return render_template("newItem.html",
                               categories=categories)


# Delete a category. Not used
# @app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def DeleteCategory(category_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    try:
        category = db_session.query(models.Category) \
                             .filter_by(id=category_id).one()
    except Exception:
        raise

    db_session.delete(category)
    db_session.commit()


@app.route('/login/', methods=['GET', 'POST'])
@catch_exceptions
def Login():
    """Main login view that supports basic form based login and OAuth login.
    OAuth logins are initiated here but a different callback view is used.
    """
    if request.method == "POST":
        # Login and validate the user.
        # user should be an instance of your `User` class
        try:
            user = db_session.query(models.User).filter_by(id=1).one()
        except NoResultFound:
            abort(404)

        login_user(user)

        flash('Logged in successfully.')

        next_url = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not auth.is_safe_url(next_url):
            return abort(400)

        return redirect(next_url or url_for("index"))
    else:
        return render_template("login.html")


@app.route("/logout/")
@login_required
def Logout():
    logout_user()
    return redirect(url_for("index"))


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return str(error), 404
    return render_template('404.html'), 404
