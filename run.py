import argparse

from item_catalog import app

# # use this if we have blueprints
# from flask import Flask, render_template, request
# from item_catalog.views import app as item_catalog
# # # Import SQLAlchemy
# # from flask.ext.sqlalchemy import SQLAlchemy
#
# # Define the WSGI application object
# app = Flask(__name__)
#
# # Configurations
# app.config.from_object('config')
#
# # Register different apps
# app.register_blueprint(item_catalog)
#
#
# # Custom 404 handler allowing different modules courtesy of
# # http://stackoverflow.com/a/28139466 (with modifications)
# @app.errorhandler(404)
# def handle_404(e):
#     path = request.path
#     # go through each blueprint to find the prefix that matches the path
#     # can't use request.blueprint since the routing didn't match anything
#     for bp_name, bp in app.blueprints.items():
#         if bp.url_prefix and path.startswith(bp.url_prefix):
#             # get the 404 handler registered by the blueprint
#             handler = app.error_handler_spec.get(bp_name, {}).get(404)
#             if handler is not None:
#                 # if a handler was found, return it's response
#                 return handler(e)
#
#     # return a default response
#     return render_template('404.html'), 404


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        type=int, help="port", default=5000)
    parser.add_argument("-i", "--ip",
                        type=str, help="host ip", default="0.0.0.0")
    args = parser.parse_args()

    app.run(host=args.ip, port=args.port)
