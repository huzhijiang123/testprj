"""
RestFul API Server
"""

import os
import sys
import eventlet

import router

# Monkey patch socket, time, select, threads
# NOTE(jokke): As per the eventlet commit
# b756447bab51046dfc6f1e0e299cc997ab343701 there's circular import happening
# which can be solved making sure the hubs are properly and fully imported
# before calling monkey_patch(). This is solved in eventlet 0.22.0 but we
# need to address it before that is widely used around.
eventlet.hubs.get_hub()
eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True, os=True)

import wsgi

def fail():
    sys.exit(-1)


def main():
    try:
        wsgi.set_eventlet_hub()
        server = wsgi.Server()

        # This equals to:
        # vi /etc/paste.ini
        #[app:server]
        #paste.app_factory = router:API.factory

        #from paste import deploy
        #server.start(deploy.loadapp("config:/etc/paste.ini", name="server"), default_port=35357)
        server.start(router.API(wsgi.APIMapper()), default_port=35357)

        server.wait()
    except:
        fail()


if __name__ == '__main__':
    main()
