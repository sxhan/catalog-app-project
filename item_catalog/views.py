from __future__ import absolute_import

import logging
from functools import wraps

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, abort

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from . import app, models


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

#############
#
# Main Route
#
#############

@app.route('/')
@app.route('/catalog/')
def index():
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
                           category=category)


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def ShowItem(category_name, item_name):
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())
    except NoResultFound:
        print "no result found!"
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)
    return str(str(category.serialize) + str(item.serialize))


@app.route('/catalog/<string:category_name>/<string:item_name>/edit/',
           methods=['GET', 'POST'])
def EditItem(category_name, item_name):
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())
    except NoResultFound:
        print "no result found!"
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)

    if request.method == 'POST':
        if 'name' in request.form and 'description' in request.form:
            item.name = request.form['name']
            item.description = request.form['description']
            flash('Successfully Edited %s' % item.name)
            return redirect(url_for('index'))

    else:
        return render_template('editItem.html',
                               category=category,
                               item=item)


@app.route('/catalog/<string:category_name>/<string:item_name>/delete/',
           methods=["GET", "POST"])
def DeleteItem(category_name, item_name):
    try:
        category, item = (
            db_session.query(models.Category, models.Item)
                      .filter(models.Category.id == models.Item.category_id)
                      .filter(models.Category.name == category_name)
                      .filter(models.Item.name == item_name).one())

        # Only owner can perform this action
        if item.user.id != session.user_id:
            return abort(403)
    except NoResultFound:
        return abort(404)
    except Exception:
        logging.error("something went wrong", exc_info=True)
        return abort(500)

    if request.method == 'POST':
        if 'confirm' in request.form and request.form["confirm"] is True:
            item_name = item.name  # Save the name for use later
            db_session.delete(item)
            db_session.commit()
            flash('Successfully Edited %s' % item_name)
            return redirect(url_for('index'))

    else:
        return render_template('deleteItem.html',
                               category=category,
                               item=item)


@app.route('/catalog/item/new/',
           methods=['GET', 'POST'])
@catch_exceptions
def NewItem():
    # This will be useful later
    categories = db_session.query(models.Category) \
                           .order_by(asc(models.Category.name))
    if request.method == 'POST':
        # Check 1: Ensure that all fields are passed back and has value
        # "If not all required fields are passed back or not all fields are "
        # "filled"
        if not all([field in request.form and request.form[field]
                    for field in ("name", "description", "category")]):
            return render_template(
                "newItem.html",
                categories=categories,
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                category=request.form.get("category", ""),
                error="All fields are required!")
        else:
            category = db_session.query(models.Category) \
                                 .filter_by(name=request.form["category"]) \
                                 .one()
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


@app.route('/login')
def login():
    return 'login page!'


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return str(error), 404
    return render_template('404.html'), 404
