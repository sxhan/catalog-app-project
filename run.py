import argparse

import flask

app = flask.Flask(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        type=int, help="port", default=5000)
    parser.add_argument("-i", "--ip",
                        type=str, help="host ip", default="0.0.0.0")
    args = parser.parse_args()

    app.config.from_object('config')
    app.run(host=args.ip, port=args.port)
