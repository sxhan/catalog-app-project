from __future__ import absolute_import

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, abort

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from . import app, models


# Connect to Database and create database session
engine = create_engine(app.config["DB_STRING"])
models.Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


#############
#
# Main Route
#
#############

@app.route('/')
def index():
    categories = db_session.query(models.Category) \
                           .order_by(asc(models.Category.name))
    return render_template('index.html',
                           categories=categories)


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


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def EditCategory(category_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    try:
        category = db_session.query(models.Category) \
                             .filter_by(id=category_id).one()
    except NoResultFound:
        return abort(404)
    except Exception:
        return abort(500)

    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % category.name)
            return redirect(url_for('index'))
    else:
        return render_template('editCategory.html', category=category)


# Delete a restaurant
@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def DeleteCategory(restaurant_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    try:
        category = db_session.query(models.Category) \
                             .filter_by(id=category_id).one()
    except NoResultFound:
        return abort(404)
    except Exception:
        return abort(500)
    if restaurantToDelete.user_id != login_session['user_id']:
        return """
               <script>
                   function myFunction() {
                       alert('you are not allowed to do this!');
                   }
               </script>
               <bodyonload='myFunction()'></body>
               """
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

@app.route('/login')
def login():
    return 'login page!'


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return str(error), 404
    return render_template('404.html'), 404
