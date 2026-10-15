"""Single-origin HTTPS exception for the separately compiled commercial profile.

This is application isolation, not a defense against replacement of the application
by a local administrator. Agricultural/browser/GDAL network access remains denied.
"""

import contextvars
import socket
from contextlib import contextmanager
from urllib.parse import urlsplit

_scope = contextvars.ContextVar("agrolines_license_connection", default=None)
_origin = None
_original_dns = socket.getaddrinfo
_original_connect = socket.socket.connect


def validate_origin(value):
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or parsed.port not in (None, 443)
    ):
        raise ValueError(
            "Origem de licenciamento deve ser HTTPS, porta 443, sem caminho ou credenciais."
        )
    return "https://" + parsed.hostname.lower()


def configure(origin):
    global _origin
    origin = validate_origin(origin)
    if _origin is not None and _origin != origin:
        raise ValueError("Origem de licenciamento já fixada.")
    _origin = origin


@contextmanager
def licensing_connection(origin):
    if _origin is None or validate_origin(origin) != _origin:
        raise PermissionError("Canal de licenciamento não habilitado neste perfil.")
    token = _scope.set({"host": urlsplit(_origin).hostname, "addresses": set()})
    try:
        yield
    finally:
        _scope.reset(token)


def guarded_dns(host, port, *args, **kwargs):
    scope = _scope.get()
    if not scope or host != scope["host"] or port != 443:
        raise PermissionError("Destino de rede não autorizado.")
    results = _original_dns(host, port, *args, **kwargs)
    scope["addresses"].update(row[4][0] for row in results)
    return results


def guarded_connect(connection, address):
    scope = _scope.get()
    if (
        not scope
        or not isinstance(address, tuple)
        or len(address) < 2
        or address[0] not in scope["addresses"]
        or address[1] != 443
    ):
        raise PermissionError("Conexão de rede não autorizada.")
    return _original_connect(connection, address)
