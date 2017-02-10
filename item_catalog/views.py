from __future__ import absolute_import

import logging
import json
import random
import string
import httplib2
from functools import wraps

from flask import (render_template, request, redirect, url_for,
                   flash, session, abort, make_response)
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
    # if 'username' not in session:
    #     return redirect('/login')
    if request.method == 'POST':
        new = models.Category(name=request.form['name'])
        db_session.add(new)
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
    # if 'username' not in session:
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
    # Anti x-site forgery attack
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state

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
        return render_template("login.html",
                               STATE=state)


@app.route("/logout/")
@login_required
def Logout():
    logout_user()
    flash("Successfully logged out!")
    return redirect(request.args.get('next') or url_for("index"))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['provider'] = 'google'  # enable this in order to use the /disconnect route
    session['credentials'] = credentials
    session['gplus_id'] = gplus_id

    print session

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Protect against cross site reference forgery attacks
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Exchange client token for a long-lived server-side token
    access_token = request.data

    # Get session info. Facebook sessio info object has the format
    # {"user": "name",
    #  "email": "email",
    #  "facebook_id": "id",
    #  "access_token": "stored_token",
    #  "picture": "picture_data"}
    session_info = auth.build_facebook_session(access_token)

    # Check if we got all the required data back. If not, flash an error
    # and return to login page
    if session_info is None:
        Logout()
        response = make_response(json.dumps("Failed to exchange access token "
                                            "for server-side token."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Add session info to session
    session["session_info"] = session_info

    # Get or create user
    user = auth.query_oauth_user(session_info['email'])
    if not user:
        user = auth.create_user(username=session_info["user"],
                                email=session_info["email"],
                                isoauth=True)

    # Login to our system
    login_user(user)

    # Return success response
    response = make_response(json.dumps(
        "Now logged in as %s" % session["session_info"]["user"]),
        200)
    response.headers['Content-Type'] = 'application/json'
    return response


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbdisconnect')
def fbdisconnect():
    """Make HTTP to Facebook to revoke access token"""
    if "facebook_id" or "access_token" not in session:
        return None
    else:
        facebook_id = session['facebook_id']
        # The access token must be included to successfully logout
        access_token = session['access_token']
        url = ('https://graph.facebook.com/%s/permissions?access_token=%s' %
               (facebook_id, access_token))
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        return result


# Add generalized disconnect function based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:  # To do this, we must add this in each of the login functions!
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showRestaurants'))

# Simple HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return str(error), 404
    return render_template('404.html'), 404
