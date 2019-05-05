from importlib import import_module

from application import app
from application.util.import_util import import_sub_module

ctrl_pkg_module = import_module('application.controller')
import_sub_module(ctrl_pkg_module)

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
