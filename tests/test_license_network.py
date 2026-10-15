"""Isolated subprocess checks avoid changing pytest's own network capabilities."""

import subprocess
import sys

import pytest

from core.license_network import validate_origin
from desktop.license_transport import LicenseTransport, NoRedirect


@pytest.mark.parametrize(
    "origin",
    [
        "http://licenses.example.test",
        "https://x.test/path",
        "https://x.test:444",
        "https://u:p@x.test",
        "https://x.test?q=1",
    ],
)
def test_insecure_or_ambiguous_license_origin_refused(origin):
    with pytest.raises(ValueError):
        validate_origin(origin)


def test_https_tls_and_redirects_cannot_silently_disable_verification():
    import ssl

    transport = LicenseTransport("https://licenses.example.test")
    handlers = transport.opener.handlers
    https = next(handler for handler in handlers if hasattr(handler, "_context"))
    assert https._context.verify_mode == ssl.CERT_REQUIRED
    assert https._context.check_hostname
    with pytest.raises(OSError, match="Redirecionamento"):
        NoRedirect().redirect_request(None, None, 302, "", {}, "http://other.test")


def test_commercial_channel_is_thread_scoped_single_origin_and_store_stays_closed():
    script = r"""
import socket
from core import license_network as n
from core.offline_policy import enforce
n._original_dns = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM,6,'',('192.0.2.1',443))]
calls=[]
n._original_connect = lambda sock, address: calls.append(address)
enforce(native=False, licensing_endpoint='https://licenses.example.test')
def denied(work):
 try: work()
 except PermissionError: return
 raise AssertionError('Network escaped policy')
denied(lambda: socket.getaddrinfo('licenses.example.test',443))
with n.licensing_connection('https://licenses.example.test'):
 denied(lambda: socket.getaddrinfo('tiles.example.test',443))
 denied(lambda: socket.getaddrinfo('licenses.example.test',80))
 socket.getaddrinfo('licenses.example.test',443)
 with socket.socket() as s:
  denied(lambda: s.connect(('192.0.2.2',443)))
  s.connect(('192.0.2.1',443))
 from concurrent.futures import ThreadPoolExecutor
 with ThreadPoolExecutor(max_workers=1) as pool:
  pool.submit(lambda: denied(lambda: socket.getaddrinfo('licenses.example.test',443))).result()
assert calls == [('192.0.2.1',443)]
denied(lambda: socket.getaddrinfo('licenses.example.test',443))
"""
    subprocess.run([sys.executable, "-c", script], check=True, timeout=30)
    # Later calls cannot turn an already-latched offline edition into the commercial profile.
    script = """
import socket
from core.offline_policy import enforce
from core.license_network import licensing_connection
enforce(native=False)
enforce(native=False, licensing_endpoint='https://licenses.example.test')
try:
 with licensing_connection('https://licenses.example.test'):
  socket.getaddrinfo('licenses.example.test',443)
except PermissionError: pass
else: raise AssertionError('Closed offline profile was re-enabled')
"""
    subprocess.run([sys.executable, "-c", script], check=True, timeout=30)
