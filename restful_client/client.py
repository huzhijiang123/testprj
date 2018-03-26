import os
import sys
import re
import http

class Client(object):
    """Client for the OpenStack Images v1 API.

    :param string endpoint: A user-supplied endpoint URL for the glance
                            service. Such as http://10.20.11.2:35357
    """
    def __init__(self, endpoint):
        """Initialize a new client for the daisy v1 API."""
        self.http_client = http.HTTPClient(endpoint)
        self.images = ImageManager(self.http_client)


class ImageManager(object):
    def __init__(self, client):
        """
        :param client: instance of BaseClient descendant for HTTP requests
        """
        self.client = client

    def delete(self, imageid):
        """Delete an image."""
        url = "/images/%s" % imageid
        resp, body = self.client.delete(url)
        print(resp) 


client = Client("http://127.0.0.1:35357")
client.images.delete("xxxxxxxx") # This is a Restful call to server URL : http://10.20.11.2:35357/images/xxxxxxxx  DELETE
