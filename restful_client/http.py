# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import logging
import socket
import requests
import six

try:
    import json
except ImportError:
    import simplejson as json

from oslo_utils import encodeutils



LOG = logging.getLogger(__name__)
USER_AGENT = 'python-daisyclient'
CHUNKSIZE = 1024 * 64  # 64kB
REQ_ID_HEADER = 'X-OpenStack-Request-ID'


def encode_headers(headers):
    """Encodes headers.
    Note: This should be used right before
    sending anything out.
    :param headers: Headers to encode
    :returns: Dictionary with encoded headers'
              names and values
    """
    return dict((encodeutils.safe_encode(h), encodeutils.safe_encode(v))
                for h, v in headers.items() if v is not None)


class _BaseHTTPClient(object):

    @staticmethod
    def _chunk_body(body):
        chunk = body
        while chunk:
            chunk = body.read(CHUNKSIZE)
            if not chunk:
                break
            yield chunk

    def _set_common_request_kwargs(self, headers, kwargs):
        """Handle the common parameters used to send the request."""

        # Default Content-Type is octet-stream
        content_type = headers.get('Content-Type', 'application/octet-stream')

        # NOTE(jamielennox): remove this later. Managers should pass json= if
        # they want to send json data.
        data = kwargs.pop("data", None)
        if data is not None and not isinstance(data, six.string_types):
            try:
                data = json.dumps(data)
                content_type = 'application/json'
            except TypeError:
                # Here we assume it's
                # a file-like object
                # and we'll chunk it
                data = self._chunk_body(data)

        headers['Content-Type'] = content_type
        kwargs['stream'] = content_type == 'application/octet-stream'
        return data

    def _handle_response(self, resp):
        if not resp.ok:
            print("Request returned failure status %s.", resp.status_code)

        content_type = resp.headers.get('Content-Type')

        # Read body into string if it isn't obviously image data
        if content_type == 'application/octet-stream':
            # Do not read all response in memory when downloading an image.
            body_iter = _close_after_stream(resp, CHUNKSIZE)
        else:
            content = resp.text
            if content_type and content_type.startswith('application/json'):
                # Let's use requests json method, it should take care of
                # response encoding
                body_iter = resp.json()
            else:
                body_iter = six.StringIO(content)
                try:
                    body_iter = json.loads(''.join([c for c in body_iter]))
                except ValueError:
                    body_iter = None

        return resp, body_iter


class HTTPClient(_BaseHTTPClient):

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        print("Init: endpoint:%s" %(self.endpoint))

    def _request(self, method, url, **kwargs):
        """Send an http request with the specified characteristics.
        Wrapper around httplib.HTTP(S)Connection.request to handle tasks such
        as setting headers and error handling.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        headers = copy.deepcopy(kwargs.pop('headers', {}))

        data = self._set_common_request_kwargs(headers, kwargs)

        # Note(flaper87): Before letting headers / url fly,
        # they should be encoded otherwise httplib will
        # complain.
        headers = encode_headers(headers)

        if self.endpoint.endswith("/") or url.startswith("/"):
            conn_url = "%s%s" % (self.endpoint, url)
        else:
            conn_url = "%s/%s" % (self.endpoint, url)

        try:
            print("Call: method:%s, conn_url:%s, data:%s, headers:%s, kwargs:%r" % (method, conn_url, data, headers, kwargs))
            resp = self.session.request(method,
                                        conn_url,
                                        data=data,
                                        headers=headers,
                                        **kwargs)
        except requests.exceptions.Timeout as e:
            message = ("Error communicating with %(url)s: %(e)s" %
                       dict(url=conn_url, e=e))
            print(message)
        except requests.exceptions.ConnectionError as e:
            message = ("Error finding address for %(url)s: %(e)s" %
                       dict(url=conn_url, e=e))
            print(message)
        except socket.gaierror as e:
            message = "Error finding address for %s: %s" % (
                self.endpoint_hostname, e)
            print(message)
        except (socket.error, socket.timeout, IOError) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s" %
                       {'endpoint': endpoint, 'e': e})
            print(message)

        resp, body_iter = self._handle_response(resp)
        return resp, body_iter

    def head(self, url, **kwargs):
        return self._request('HEAD', url, **kwargs)

    def get(self, url, **kwargs):
        return self._request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self._request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self._request('PUT', url, **kwargs)

    def patch(self, url, **kwargs):
        return self._request('PATCH', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._request('DELETE', url, **kwargs)


def _close_after_stream(response, chunk_size):
    """Iterate over the content and ensure the response is closed after."""
    # Yield each chunk in the response body
    for chunk in response.iter_content(chunk_size=chunk_size):
        yield chunk
    # Once we're done streaming the body, ensure everything is closed.
    # This will return the connection to the HTTPConnectionPool in urllib3
    # and ideally reduce the number of HTTPConnectionPool full warnings.
    response.close()



