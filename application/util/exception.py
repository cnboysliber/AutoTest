import sys
import traceback

from flask import jsonify
from functools import wraps
from application import app

if not app.config['DEBUG']:
    from application.util import logger as LOGGER
else:
    from application.util import LocalLogger as LOGGER


def try_except(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_str = 'Function name: {0}; Error info: {1}: {2}; Traceback: {3}'\
                .format(str(fn.__name__),
                        str(e.__class__.__name__),
                        str(e),
                        str(traceback.extract_tb(exc_tb)))
            # 正式环境，记录错误日志并返回错误信息
            if not app.config['DEBUG']:
                LOGGER.exception_log(error_str)
                return jsonify({'success': False, 'error': str(e)})
            # 测试环境直接raise
            else:
                raise
    return wrapped
