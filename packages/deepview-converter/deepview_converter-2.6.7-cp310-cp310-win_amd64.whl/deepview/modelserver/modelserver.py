# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import logging
import os
import sys
import tempfile
from deepview.converter import plugin_manager
from deepview.converter.plugin_api.params import reserved_params_list

import deepview.converter.convert as deepview_convert
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import current_app
from io import StringIO

app = Flask(__name__)
cors = CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 Mb limit

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)


class CaptureOutput(object):
    def __init__(self):
        self.capture = StringIO()
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        self.close()

    def __enter__(self):
        pass # No current implementation needed

    def __exit__(self, *args):
        self.close()

    def close(self):
        if self.stdout is not None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.capture is not None:
            self.capture.close()
            self.capture = None

    def write(self, data):
        self.capture.write(data)
        self.stdout.write(data)

    def flush(self):
        self.capture.flush()
        self.stdout.flush()


class NodeHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

        self.nodes = []

    def emit(self, record):
        msg = self.format(record)
        if msg.startswith("Node name:"):
            self.nodes.append(msg[11:])


@app.route("/")
def index():
    """
    Display README.md on root page
    :return:
    """
    return app.send_static_file("index.html")

@app.route("/plugins", methods=["GET"])
def get_plugins():
    try:
        list = deepview_convert.get_plugins()
        resp = jsonify({"plugins": list})
        resp.status_code = 200
        
    except Exception as e:
        resp = jsonify({"reply": str(e.args)})
        resp.status_code = 400
        print('ERROR:'+ str(e.args))
    
    return resp


@app.route("/plugins/help", methods=["GET"])
def get_help():

    try:

        name = request.args.get('name')
        src = request.args.get('source')
        dst = request.args.get('dest')

        if name is None or src is None or dst is None:
            resp = jsonify({"reply": "usage: url/plugins/help?name=NAME&source=SRC&dest=DEST"})
            resp.status_code = 200
            return resp

        list = deepview_convert.get_params(name,src,dst)

        resp = jsonify({"params": list})
        resp.status_code = 200
        
    except Exception as e:
        resp = jsonify({"reply": "usage: url/plugins/help?name=NAME&source=SRC&dest=DEST"})
        resp.status_code = 200
    
    return resp

@app.route("/plugins/reserved", methods=["GET"])
def get_reserved_list():
    try:

        list = reserved_params_list
        resp = jsonify(list)
        resp.status_code = 200
        
    except Exception as e:
        resp = jsonify({"reply": "usage: url/plugins/help?name=NAME&source=SRC&dest=DEST"})
        resp.status_code = 200
    
    return resp

@app.route("/plugins/install", methods=["GET"])
def install_plugins():
    try:
        package = request.args.get('package')
        if package is None:
            resp = jsonify({'success':'no', 'reply': 'usage: url/plugins/install?package=pakcage_path'})
            resp.status_code = 400
        else:
            output = deepview_convert.install(package,False)
            resp = jsonify({"response": output})
            resp.status_code = 200
        
    except Exception as e:
        resp = jsonify({"reply": str(e.args)})
        resp.status_code = 400
        print('ERROR:'+ str(e.args))
    
    return resp

@app.route("/plugins/uninstall", methods=["GET"])
def uninstall_plugins():
    try:
        package = request.args.get('package')
        if package is None:
            resp = jsonify({'success':'no', 'reply': 'Syntax package=pakcage_name'})
            resp.status_code = 400
        else:
            output = deepview_convert.uninstall(package,False)
            resp = jsonify({"response": output})
            resp.status_code = 200
        
    except Exception as e:
        resp = jsonify({"reply": str(e.args)})
        resp.status_code = 400
        print('ERROR:'+ str(e.args))
    
    return resp

@app.route("/convert", methods=["POST"])
def convert():
    """
    convert command:
    paramtertes in JSON
    """
    try:
        
        if request.is_json:
            params = request.get_json()
            output = deepview_convert.convert(params)
            resp = jsonify(output)
            resp.status_code = 200
        else:
            resp = jsonify({'success':'no', 'reply': 'Paramaters missing as JSON payload'})
            resp.status_code = 400
            
    except Exception as e:
        resp = jsonify({"reply": str(e.args)})
        resp.status_code = 400
        print('ERROR:'+ str(e.args))
    
    return resp

def str_to_bool(s):
    if isinstance(s,str):
        if s.lower() == "true":
            return True
        else:
            return False

def main():
    app.run(host='127.0.0.1', port=10816, debug=False)

if __name__ == "__main__":
    main()
