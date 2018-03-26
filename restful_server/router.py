import images
import wsgi


class API(wsgi.Router):

    """WSGI router for Glance v1 API requests."""

    def __init__(self, mapper):
        images_resource = images.create_resource()

        mapper.connect("/images",
                       controller=images_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/images/{id}",
                       controller=images_resource,
                       action="show",
                       conditions=dict(method=["GET"]))
        mapper.connect("/images/{id}",
                       controller=images_resource,
                       action="update",
                       conditions=dict(method=["PUT"]))
        mapper.connect("/images/{id}",
                       controller=images_resource,
                       action="delete",
                       conditions=dict(method=["DELETE"]))

        super(API, self).__init__(mapper)
