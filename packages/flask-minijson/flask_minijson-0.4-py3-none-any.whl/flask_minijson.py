import typing as tp

import minijson
from flask import Flask

try:
    from flask_json import JsonRequest
except ImportError:
    # we must be running on a newer version of Flask-JSON
    from flask_json import FlaskJSONRequest as JsonRequest


MINIJSON_MIME = ('application/minijson', 'application/x-minijson')


class MiniJSONRequest(JsonRequest):
    def get_json(self, force=False, silent=False, cache=True):
        """
        Return JSON data, if content type is application/minijson it will be loaded
        via minijson, else it will be loaded the normal way.
        """
        if self.headers.get('Content-Type') in MINIJSON_MIME:
            return minijson.loads(self.get_data())
        else:
            return super().get_json(force, silent, cache)


class FlaskMiniJSON(object):
    """Flask-MiniJSON extension class."""
    def __init__(self, app: tp.Optional[Flask] = None):
        self._app = app
        self._error_handler_func = None
        self._decoder_error_func = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if 'json' not in app.extensions:
            raise RuntimeError('flask-json must be initialized before MiniJSON!')
        app.extensions['minijson'] = self

        self._app = app
        app.request_class = MiniJSONRequest
