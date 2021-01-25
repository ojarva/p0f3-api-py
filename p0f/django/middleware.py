"""
Adds p0f attribute to request object.

To enable, add

  'p0f.django.middleware.P0fMiddleware',

to "MIDDLEWARE_CLASSES" in your project's settings.py. Also, add

  P0FSOCKET="/path/to/p0f_socket"

to the same file.

Start p0f with "-s /path/to/p0f_socket".
"""

import logging
import socket

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed

import p0f

log = logging.getLogger(__name__)


class P0fMiddleware:  # pylint: disable=too-few-public-methods
    """ Adds "p0f" attribute to request. Requires P0FSOCKET setting in Django settings.py """
    def __init__(self):
        try:
            enabled = settings.P0FENABLED
            if not enabled:
                raise MiddlewareNotUsed
        except AttributeError:
            pass

        try:
            settings.P0FSOCKET
        except AttributeError as ex:
            log.error("P0FSOCKET is not configured.")
            raise ImproperlyConfigured(
                "P0FSOCKET is not configured. This middleware does not run without path to p0f unix socket"
            ) from ex

    def process_request(self, request):
        remote_info = None
        try:
            p0fapi = p0f.P0f(settings.P0FSOCKET)
            remote_info = p0fapi.get_info(request.META.get("REMOTE_ADDR"))
        except socket.error as e:
            log.error("p0f API call returned %r", e)
        except KeyError as e:
            log.warning("No data available for %s - is p0f listening the right interface?", request.META.get("REMOTE_ADDR"))
        except (ValueError, p0f.P0fException) as e:
            log.warning("internal error: %r", e)

        request.p0f = remote_info
