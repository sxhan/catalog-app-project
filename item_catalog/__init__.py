import sys
import logging

from flask import Flask
from flaskext.csrf import csrf


# Define the WSGI application object
app = Flask(__name__,
            static_folder="static",
            template_folder="templates")

# Configurations
app.config.from_object('config')
# Override configs
app.config.from_pyfile(app.instance_path + "/" + "config.py")

# Enable CSRF protection
csrf(app)

# Walk all configs and if any of them are None, then it means the user didn't
# Add a required custom config (eg. FB access key. Throw error and exit)
for config in app.config["REQUIRED_CUSTOM_CONFIGS"]:
    if config not in app.config or app.config[config] is None:
        logging.critical("Application is incorrectly configured! Local config "
                         "for config%s is missing" % {"config": config})
        sys.exit(1)

# Sketchy Flask circular import hack to load views
from . import views
