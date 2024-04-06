# SPDX-License-Identifier: Apache-2.0

import base64
import json
import logging
import os
import ssl
import sys
import urllib.request
from typing import Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
# logging.getLogger().setLevel(logging.DEBUG)


class Error(Exception):
    pass


class LoginError(Error):
    def __init__(self, message: str) -> None:
        self.message = message


class GetError(Error):
    def __init__(self, message: str) -> None:
        self.message = message


class PostError(Error):
    def __init__(self, message: str) -> None:
        self.message = message


class ApiSSLContext(ssl.SSLContext):
    def __new__(cls, hostname, **kwargs):
        return super(ApiSSLContext, cls).__new__(cls, ssl.PROTOCOL_TLS_CLIENT, **kwargs)

    def __init__(self, hostname, **kwargs):
        super(ApiSSLContext, self).__init__()
        self._server_hostname = hostname
        self.options |= ssl.OP_NO_SSLv2
        self.options |= ssl.OP_NO_SSLv3
        self.verify_mode = ssl.CERT_REQUIRED
        self.check_hostname = True

    def wrap_socket(self, *args, **kwargs):
        if self._server_hostname is not None:
            kwargs['server_hostname'] = self._server_hostname
        return super().wrap_socket(*args, **kwargs)


class Session(object):
    def __init__(self, host: str,
                 token: str,
                 ssl_context: Optional[ssl.SSLContext] = None,
                 user_agent: Optional[str] = None,
                 server_hostname: Optional[str] = None) -> None:
        self._server_hostname = server_hostname
        self._base_url = urlparse(host)
        self._volga_ws_url = f"wss://{self._base_url.netloc}/v1/ws/volga"
        self._token = token
        if ssl_context:
            if server_hostname is not None:
                raise ValueError("server_hostname is not applicable when"
                                 " using custom ssl_context")
            self._ssl_context = ssl_context
        else:
            self._ssl_context = create_ssl_context(server_hostname)
        self._user_agent = user_agent

    def auth_header(self) -> Dict[str, str]:
        header = {"Authorization": "Bearer {}".format(self._token)}
        if self._user_agent:
            header['User-Agent'] = self._user_agent
        return header

    def get_token(self) -> str:
        return self._token

    def get_base_url(self) -> str:
        return self._base_url

    def get_user_agent(self) -> str:
        return self._user_agent

    def get_volga_ws_url(self) -> str:
        return self._volga_ws_url

    def get_ssl_context(self):
        return self._ssl_context

    def get_server_hostname(self) -> str:
        return self._server_hostname


def create_ssl_context(server_hostname=None):
    c = ApiSSLContext(server_hostname)
    c.verify_mode = ssl.CERT_REQUIRED
    c.check_hostname = True
    if 'API_CA_CERT' in os.environ:
        c.load_verify_locations(cadata=os.environ['API_CA_CERT'])
    else:
        c.load_default_certs(ssl.Purpose.SERVER_AUTH)
    if hasattr(c, 'keylog_filename'):
        keylogfile = os.environ.get('SSLKEYLOGFILE')
        if keylogfile and not sys.flags.ignore_environment:
            c.keylog_filename = keylogfile
    return c


def get_request(session: Session, url, user_agent=None, ssl_context=None, headers=None):
    return _send_request('GET', session, url, None, user_agent, ssl_context, headers)


def post_request(session: Session, url, payload, user_agent=None, ssl_context=None, headers=None):
    return _send_request('POST', session, url, payload, user_agent, ssl_context, headers)


def put_request(session: Session, url, payload, user_agent=None, ssl_context=None, headers=None):
    return _send_request('PUT', session, url, payload, user_agent, ssl_context, headers)


def _send_request(method, session: Session, url, payload, user_agent, ssl_context, headers):
    if headers is None:
        headers = {}
    if 'Accept' not in headers:
        headers['Accept'] = 'application/json'
    if session:
        if user_agent is None:
            user_agent = session.get_user_agent()
        if ssl_context is None:
            ssl_context = session.get_ssl_context()
        headers['Authorization'] = 'Bearer ' + session.get_token()
        url = urllib.parse.urljoin(session.get_base_url().geturl(), url)
    if user_agent:
        headers['User-Agent'] = user_agent
    if payload is None:
        data = None
        logger.debug('%s request url %s', method, url)
    else:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode()
        logger.debug('%s request url %s, payload %s', method, url, data)
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    with urllib.request.urlopen(req, context=ssl_context) as response:
        return (response.getcode(),
                response.msg,
                response.getheaders(),
                response.read().decode('utf-8'))


def approle_login(host: str,
                  role_id: str | None,
                  secret_id: str,
                  user_agent: Optional[str] = None,
                  server_hostname: Optional[str] = None):
    try:
        payload = {'secret-id': secret_id}
        if role_id is not None:
            payload['role-id'] = role_id
        base_url = urlparse(host)
        url = base_url.geturl() + '/v1/approle-login'
        sslc = create_ssl_context(server_hostname)
        (_code, msg, _headers, body) = post_request(
            None, url, payload, user_agent, sslc)
        del payload['secret-id']
        if msg != 'OK':
            raise LoginError('Approle login failed: ' + msg)
        return Session(host, json.loads(body)['token'], sslc,
                       user_agent=user_agent)
    except urllib.error.HTTPError as e:
        raise LoginError('Exception during approle_login: ' +
                         get_error(e)) from e
    except urllib.error.URLError as e:
        raise LoginError('Exception during approle_login: ' +
                         get_error(e)) from e
    except Exception as e:
        raise LoginError('Exception during approle_login') from e


def get_error(e):
    try:
        body = json.loads(e.__dict__['file'].read().decode('utf-8'))
        return body['errors'][0]['error-message']
    except Exception:
        return "unknown"


def kubernetes_login(host: str,
                     tenant: str,
                     service: str,
                     role: str,
                     jwt: str,
                     user_agent: Optional[str] = None,
                     check_hostname: bool = True,
                     server_hostname: Optional[str] = None):
    try:
        payload = {"tenant": tenant,
                   "service": service,
                   "role": role,
                   "jwt": jwt}
        base_url = urlparse(host)
        url = base_url.geturl() + '/v1/kubernetes-login'
        sslc = create_ssl_context(server_hostname)
        sslc.check_hostname = check_hostname
        (_code, msg, _headers, body) = post_request(
            None, url, payload, user_agent, sslc)
        if msg != 'OK':
            raise LoginError("Kubernetes login failed: " + msg)
        return Session(host, json.loads(body)['token'], sslc,
                       user_agent=user_agent)
    except urllib.error.HTTPError as e:
        raise LoginError('Exception during kubernetes_login: ' +
                         get_error(e)) from e
    except urllib.error.URLError as e:
        raise LoginError('Exception during kubernetes_login ' +
                         get_error(e)) from e
    except Exception as e:
        raise LoginError('Exception during kubernetes_login') from e


def login(host: str,
          username: str,
          password: str,
          tenant: Optional[str] = None,
          user_agent: Optional[str] = None,
          server_hostname: Optional[str] = None) -> Session:
    try:
        payload = {'username': username,
                   'password': password}
        if tenant:
            payload['tenant'] = tenant

        base_url = urlparse(host)
        url = base_url.geturl() + '/v1/login'
        sslc = create_ssl_context(server_hostname)
        (_code, msg, _headers, body) = post_request(
            None, url, payload, user_agent, sslc)
        del payload['password']
        if msg != "OK":
            raise LoginError('Login failed: ' + msg)
        return Session(host, json.loads(body)['token'], sslc,
                       user_agent=user_agent)
    except urllib.error.HTTPError as e:
        raise LoginError('Exception during login: ' +
                         get_error(e)) from e
    except urllib.error.URLError as e:
        raise LoginError('Exception during login ' +
                         get_error(e)) from e
    except Exception as e:
        raise LoginError('Exception during login') from e


# Example Strongbox integrations

def get_secret(session: Session,
               vault_name: str,
               secret_name: str) -> Dict[str, str]:
    url = "{}/v1/state/strongbox/vaults/{}/secrets/{}".format(
        session.get_base_url().geturl(), vault_name, secret_name)
    (_code, msg, _headers, body) = get_request(session, url)
    if msg != 'OK':
        raise GetError('Get secret failed: ' + msg)
    return json.loads(body)['dict']


def encrypt(session: Session, key_name: str, plain_text: str) -> str:
    url = "{}/v1/state/strongbox/transit-keys/{}/encrypt".format(
        session.get_base_url().geturl(), key_name)
    payload = {
        "plaintext": str(base64.b64encode(plain_text.encode('utf-8')),
                         'utf-8')
    }
    (_code, msg, _headers, body) = post_request(session, url, payload)
    del payload['plaintext']
    if msg != "OK":
        raise PostError("Encrypt failed: " + msg)
    return json.loads(body)["ciphertext"]


def decrypt(session: Session, key_name: str, cipher_text: str) -> str:
    url = "{}/v1/state/strongbox/transit-keys/{}/decrypt".format(
        session.get_base_url().geturl(), key_name)
    payload = {
        "ciphertext": cipher_text,
    }
    (_code, msg, _headers, body) = post_request(session, url, payload)
    if msg != "OK":
        raise PostError("Decrypt failed: " + msg)
    return str(base64.b64decode(json.loads(body)["plaintext"]),
               'utf-8')
