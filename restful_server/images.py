"""
/images endpoint for Glance v1 API
"""

import copy

from webob.exc import HTTPBadRequest
from webob.exc import HTTPConflict
from webob.exc import HTTPForbidden
from webob.exc import HTTPMethodNotAllowed
from webob.exc import HTTPNotFound
from webob.exc import HTTPRequestEntityTooLarge
from webob.exc import HTTPServiceUnavailable
from webob.exc import HTTPUnauthorized
from webob import Response

import wsgi

class Controller(object):
    """
    WSGI controller for images resource in Glance v1 API
    The images resource API is a RESTful web service for image data. The API
    is as follows::
        GET /images -- Returns a set of brief metadata about images
        GET /images/detail -- Returns a set of detailed metadata about
                              images
        HEAD /images/<ID> -- Return metadata about an image with id <ID>
        GET /images/<ID> -- Return image data for image with id <ID>
        POST /images -- Store image data and return metadata about the
                        newly-stored image
        PUT /images/<ID> -- Update image metadata and/or upload image
                            data for a previously-reserved image
        DELETE /images/<ID> -- Delete the image with id <ID>
    """

    def __init__(self):
        pass

    def create(self, req, image_meta, image_data):
        return {'image_meta': "aaa"}

    def update(self, req, id, image_meta, image_data):
        return {'image_meta': "bbb"}

    def delete(self, req, id):
        return Response(body='', status=200)

class ImageDeserializer(wsgi.JSONRequestDeserializer):
    """Handles deserialization of specific controller method requests."""

    def create(self, request):
        return request

    def update(self, request):
        return request


class ImageSerializer(wsgi.JSONResponseSerializer):
    """Handles serialization of specific controller method responses."""

    def __init__(self):
        pass

    def meta(self, response, result):
        return response

    def show(self, response, result):
        return response

    def update(self, response, result):
        return response

    def create(self, response, result):
        return response


def create_resource():
    """Images resource factory method"""
    deserializer = ImageDeserializer()
    serializer = ImageSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)
