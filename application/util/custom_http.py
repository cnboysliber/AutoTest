import os
import datetime
import socket
import warnings
import logging
import requests
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
from urllib3.connection import (
    HTTPConnection,
    DummyConnection
)
from socket import error as SocketError, timeout as SocketTimeout
from urllib3.exceptions import *
from urllib3.connectionpool import (HTTPConnectionPool, HTTPSConnectionPool)
try:
    from urllib3.contrib import appengine
except (ImportError, AttributeError):
    from urllib3.contrib import _appengine_environ as appengine

try:  # Compiled with SSL?
    import ssl
    BaseSSLError = ssl.SSLError
except (ImportError, AttributeError):  # Platform-specific: No SSL.
    ssl = None

    class BaseSSLError(BaseException):
        pass

from urllib3.util.ssl_ import (
    resolve_cert_reqs,
    resolve_ssl_version,
    assert_fingerprint,
    create_urllib3_context,
    ssl_wrap_socket
)
from application.util.implementation import *

DEFAULT_POOLBLOCK = False

log = logging.getLogger(__name__)
port_by_scheme = {
    'http': 80,
    'https': 443,
}
RECENT_DATE = datetime.date(2017, 6, 30)


class MyHTTPConnection(HTTPConnection):
    def _new_conn(self):
        """ Establish a socket connection and set nodelay settings on it.

        :return: New socket connection.
        """
        extra_kw = {}
        if self.source_address:
            extra_kw['source_address'] = self.source_address

        if self.socket_options:
            extra_kw['socket_options'] = self.socket_options

        try:
            conn = self.create_connection(
                (self.host, self.port), self.timeout, **extra_kw)

        except SocketTimeout as e:
            raise ConnectTimeoutError(
                self, "Connection to %s timed out. (connect timeout=%s)" %
                (self.host, self.timeout))

        except SocketError as e:
            raise NewConnectionError(
                self, "Failed to establish a new connection: %s" % e)

        return conn

    def create_connection(self, address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                          source_address=None, socket_options=None):
        """Connect to *address* and return the socket object.

        Convenience function.  Connect to *address* (a 2-tuple ``(host,
        port)``) and return the socket object.  Passing the optional
        *timeout* parameter will set the timeout on the socket instance
        before attempting to connect.  If no *timeout* is supplied, the
        global default timeout setting returned by :func:`getdefaulttimeout`
        is used.  If *source_address* is set it must be a tuple of (host, port)
        for the socket to bind as a source address before making the connection.
        An host of '' or port 0 tells the OS to use the default.
        """
        host, port = address
        if host.startswith('['):
            host = host.strip('[]')
        err = None

        # Using the value from allowed_gai_family() in the context of getaddrinfo lets
        # us select whether to work with IPv4 DNS records, IPv6 records, or both.
        # The original create_connection function always returns all records.
        family = self.allowed_gai_family()
        for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)

                # If provided, set socket level options before connecting.
                self._set_socket_options(sock, socket_options)

                if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                    sock.settimeout(timeout)
                # if source_address:
                #     sock.bind(source_address)
                if source_address:
                    sock.connect((source_address, sa[-1]))
                else:
                    sock.connect(sa)
                return sock

            except socket.error as e:
                err = e
                if sock is not None:
                    sock.close()
                    # sock = None

        if err is not None:
            raise err

        raise socket.error("getaddrinfo returns an empty list")

    @staticmethod
    def _set_socket_options(sock, options):
        if options is None:
            return

        for opt in options:
            sock.setsockopt(*opt)

    @staticmethod
    def allowed_gai_family():
        """This function is designed to work in the context of
        getaddrinfo, where family=socket.AF_UNSPEC is the default and
        will perform a DNS search for both IPv6 and IPv4 records."""

        family = socket.AF_INET
        if HAS_IPV6:
            family = socket.AF_UNSPEC
        return family


class HTTPSConnection(MyHTTPConnection):
    default_port = port_by_scheme['https']

    ssl_version = None

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 ssl_context=None, server_hostname=None, **kw):

        HTTPConnection.__init__(self, host, port, strict=strict,
                                timeout=timeout, **kw)

        self.key_file = key_file
        self.cert_file = cert_file
        self.ssl_context = ssl_context
        self.server_hostname = server_hostname

        # Required property for Google AppEngine 1.9.0 which otherwise causes
        # HTTPS requests to go out as HTTP. (See Issue #356)
        self._protocol = 'https'

    def connect(self):
        conn = self._new_conn()
        self._prepare_conn(conn)

        if self.ssl_context is None:
            self.ssl_context = create_urllib3_context(
                ssl_version=resolve_ssl_version(None),
                cert_reqs=resolve_cert_reqs(None),
            )

        self.sock = ssl_wrap_socket(
            sock=conn,
            keyfile=self.key_file,
            certfile=self.cert_file,
            ssl_context=self.ssl_context,
            server_hostname=self.server_hostname
        )


class MyVerifiedHTTPSConnection(HTTPSConnection):
    """
    Based on httplib.HTTPSConnection but wraps the socket with
    SSL certification.
    """
    cert_reqs = None
    ca_certs = None
    ca_cert_dir = None
    ssl_version = None
    assert_fingerprint = None

    def set_cert(self, key_file=None, cert_file=None,
                 cert_reqs=None, ca_certs=None,
                 assert_hostname=None, assert_fingerprint=None,
                 ca_cert_dir=None):
        """
        This method should only be called once, before the connection is used.
        """
        # If cert_reqs is not provided, we can try to guess. If the user gave
        # us a cert database, we assume they want to use it: otherwise, if
        # they gave us an SSL Context object we should use whatever is set for
        # it.
        if cert_reqs is None:
            if ca_certs or ca_cert_dir:
                cert_reqs = 'CERT_REQUIRED'
            elif self.ssl_context is not None:
                cert_reqs = self.ssl_context.verify_mode

        self.key_file = key_file
        self.cert_file = cert_file
        self.cert_reqs = cert_reqs
        self.assert_hostname = assert_hostname
        self.assert_fingerprint = assert_fingerprint
        self.ca_certs = ca_certs and os.path.expanduser(ca_certs)
        self.ca_cert_dir = ca_cert_dir and os.path.expanduser(ca_cert_dir)

    def connect(self):
        # Add certificate verification
        conn = self._new_conn()
        hostname = self.host

        if self._tunnel_host:
            self.sock = conn
            # Calls self._set_hostport(), so self.host is
            # self._tunnel_host below.
            self._tunnel()
            # Mark this connection as not reusable
            self.auto_open = 0

            # Override the host with the one we're requesting data from.
            hostname = self._tunnel_host

        server_hostname = hostname
        if self.server_hostname is not None:
            server_hostname = self.server_hostname

        is_time_off = datetime.date.today() < RECENT_DATE
        if is_time_off:
            warnings.warn((
                'System time is way off (before {0}). This will probably '
                'lead to SSL verification errors').format(RECENT_DATE),
                SystemTimeWarning
            )

        # Wrap socket using verification with the root certs in
        # trusted_root_certs
        if self.ssl_context is None:
            self.ssl_context = create_urllib3_context(
                ssl_version=resolve_ssl_version(self.ssl_version),
                cert_reqs=resolve_cert_reqs(self.cert_reqs),
            )

        context = self.ssl_context
        context.verify_mode = resolve_cert_reqs(self.cert_reqs)
        self.sock = ssl_wrap_socket(
            sock=conn,
            keyfile=self.key_file,
            certfile=self.cert_file,
            ca_certs=self.ca_certs,
            ca_cert_dir=self.ca_cert_dir,
            server_hostname=server_hostname,
            ssl_context=context)

        if self.assert_fingerprint:
            assert_fingerprint(self.sock.getpeercert(binary_form=True),
                               self.assert_fingerprint)
        elif context.verify_mode != ssl.CERT_NONE \
                and not getattr(context, 'check_hostname', False) \
                and self.assert_hostname is not False:
            # While urllib3 attempts to always turn off hostname matching from
            # the TLS library, this cannot always be done. So we check whether
            # the TLS Library still thinks it's matching hostnames.
            cert = self.sock.getpeercert()
            if not cert.get('subjectAltName', ()):
                warnings.warn((
                    'Certificate for {0} has no `subjectAltName`, falling back to check for a '
                    '`commonName` for now. This feature is being removed by major browsers and '
                    'deprecated by RFC 2818. (See https://github.com/shazow/urllib3/issues/497 '
                    'for details.)'.format(hostname)),
                    SubjectAltNameWarning
                )
            _match_hostname(cert, self.assert_hostname or server_hostname)

        self.is_verified = (
            context.verify_mode == ssl.CERT_REQUIRED or
            self.assert_fingerprint is not None
        )


def _match_hostname(cert, asserted_hostname):
    try:
        match_hostname(cert, asserted_hostname)
    except CertificateError as e:
        log.error(
            'Certificate did not match expected hostname: %s. '
            'Certificate: %s', asserted_hostname, cert
        )
        # Add cert to exception and reraise so client code can inspect
        # the cert when catching the exception, if they want to
        e._peer_cert = cert
        raise


def _has_ipv6(host):
    """ Returns True if the system can bind an IPv6 address. """
    sock = None
    has_ipv6 = False

    # App Engine doesn't support IPV6 sockets and actually has a quota on the
    # number of sockets that can be used, so just early out here instead of
    # creating a socket needlessly.
    # See https://github.com/urllib3/urllib3/issues/1446
    if appengine.is_appengine_sandbox():
        return False

    if socket.has_ipv6:
        # has_ipv6 returns true if cPython was compiled with IPv6 support.
        # It does not tell us if the system has IPv6 support enabled. To
        # determine that we must bind to an IPv6 address.
        # https://github.com/shazow/urllib3/pull/611
        # https://bugs.python.org/issue658327
        try:
            sock = socket.socket(socket.AF_INET6)
            sock.bind((host, 0))
            has_ipv6 = True
        except Exception:
            pass

    if sock:
        sock.close()
    return has_ipv6


HAS_IPV6 = _has_ipv6('::1')


if ssl:
    # Make a copy for testing.
    UnverifiedHTTPSConnection = HTTPSConnection
    MyHTTPSConnection = MyVerifiedHTTPSConnection
else:
    MyHTTPSConnection = DummyConnection


class MyHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = MyHTTPSConnection

    def _prepare_conn(self, conn):
        """
        Prepare the ``connection`` for :meth:`urllib3.util.ssl_wrap_socket`
        and establish the tunnel if proxy is used.
        """

        if isinstance(conn, MyVerifiedHTTPSConnection):
            conn.set_cert(key_file=self.key_file,
                          cert_file=self.cert_file,
                          cert_reqs=self.cert_reqs,
                          ca_certs=self.ca_certs,
                          ca_cert_dir=self.ca_cert_dir,
                          assert_hostname=self.assert_hostname,
                          assert_fingerprint=self.assert_fingerprint)
            conn.ssl_version = self.ssl_version
        return conn


class MyHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = MyHTTPConnection


pool_classes_by_scheme_new = {
    'http': MyHTTPConnectionPool,
    'https': MyHTTPSConnectionPool,
}


class MyPoolManager(PoolManager):
    def __init__(self, num_pools=10, headers=None, **connection_pool_kw):

        PoolManager.__init__(self, num_pools=num_pools, headers=headers, **connection_pool_kw)
        self.pool_classes_by_scheme = pool_classes_by_scheme_new


class CustomAdapter(HTTPAdapter):
    def __init__(self, source_address=None, ):
        self.source_address = source_address
        super(CustomAdapter, self).__init__()

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        """Initializes a urllib3 PoolManager.

        This method should not be called from user code, and is only
        exposed for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param connections: The number of urllib3 connection pools to cache.
        :param maxsize: The maximum number of connections to save in the pool.
        :param block: Block when no free connections are available.
        :param pool_kwargs: Extra keyword arguments used to initialize the Pool Manager.
        """
        # save these values for pickling
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = MyPoolManager(num_pools=connections, maxsize=maxsize,
                                         block=block, strict=True,
                                         source_address=self.source_address, **pool_kwargs)


if __name__ == '__main__':
    url = 'https://bid.huishoubao.com/api/handle'
    body = {
        "_head": {
            "_version": "0.01",
            "_msgType": "request",
            "_timestamps": 1551167757,
            "_invokeId": "auction1551167757673",
            "_callerServiceId": "110008",
            "_groupNo": "1",
            "_interface": "SalesServer.Api.User.RefundList",
            "_remark": "request"
        },
        "_param": {
            "userId": 1,
            "pageIndex": 0,
            "pageSize": 10
        }
    }
    with requests.session() as session:
        session.mount('https://', CustomAdapter(source_address='118.89.42.94'))
        res = session.post(url, json=body)
        print(res.status_code, res.json())
