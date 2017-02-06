from flask import Flask

# Define the WSGI application object
app = Flask(__name__,
            static_folder="static",
            template_folder="templates")

# Configurations
app.config.from_object('config')

# Sketchy Flask circular import hack to load views
from . import views
