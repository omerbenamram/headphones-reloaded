from six import PY2, PY3

if PY2:
    from .http import HTTPStatus
if PY3:
    # noinspection PyCompatibility
    from http import HTTPStatus
