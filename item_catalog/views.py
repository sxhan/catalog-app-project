from flask import Blueprint, render_template


app = Blueprint('item_catalog', __name__,
                template_folder='templates',
                static_folder="static")


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/login')
def login():
    return 'login page!'


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return str(error), 404
    return render_template('404.html'), 404
