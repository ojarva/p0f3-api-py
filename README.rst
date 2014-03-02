p0f Python API client
=====================

This is a simple API client for p0f3, available at 
http://lcamtuf.coredump.cx/p0f3/ . It is not compatible with version 2.x 
or 1.x. Start p0f with ``-s path/to/unix_socket`` option.

Basic usage:

::

  from p0f import P0f, P0fException

  data = None
  p0f = P0f("p0f.sock") # point this to socket defined with "-s" argument.
  try:
      data = p0f.get_info("192.168.0.1")
  except P0fException, e:
      # Invalid query was sent to p0f. Maybe the API has changed?
      print e
  except KeyError, e:
      # No data is available for this IP address.
      print e
  except ValueError, e:
      # p0f returned invalid constant values. Maybe the API has changed?
      print e

  if data:
      print "First seen:", data["first_seen"]
      print "Last seen:", data["last_seen"]


Django integration
------------------

See examples/django_models.py for complete Django model of the data returned by p0f.

Django middleware is available in ``p0f.django.middleware``.

To use, add ``P0FSOCKET = "path/to/p0f_unix_socket"`` to your project's settings.py,
and ``p0f.django.middleware.P0fMiddleware`` to ``MIDDLEWARE_CLASSES``.

The middleware adds ``p0f`` attribute to all incoming requests. ``request.p0f`` is
None if connection to p0f failed or p0f did not return data for remote IP address.

Data fields
-----------

Parts of these descriptions are shamelessly copied from 
http://lcamtuf.coredump.cx/p0f3/README :

By default, following fields are parsed:

- datetime: **first_seen**
- datetime: **last_seen**
- timedelta: **uptime**
- int: **uptime_sec**
- timedelta: **up_mod_days**
- datetime: **last_nat**
- datetime: **last_chg**

Additionally, **bad_sw** and **os_match_q** are validated. "ValueError"
is raised, if incorrect value is encountered. For all empty fields,
None is used instead of empty strings or constants:

- **uptime_min**
- **uptime_sec**
- **uptime**
- **up_mod_days**
- **last_nat**
- **last_chg**
- **distance**
- **bad_sw**
- **os_name**
- **os_flavor**
- **http_flavor**
- **link_type**
- **language**

This parsing and validation can be disabled with

::

  p0f.get_info("192.168.0.1", True)

Full descriptions of the fields:

- int: **first_seen** - unix time (seconds) of first observation of the host.
- int: **last_seen**  - unix time (seconds) of most recent traffic.
- int: **total_conn** - total number of connections seen.
- int: **uptime_min** - calculated system uptime, in minutes. Zero if not known.
- int: **up_mod_days** - uptime wrap-around interval, in days.
- int: **last_nat**    - time of the most recent detection of IP sharing (NAT, load balancing, proxying). Zero if never detected.
- int: **last_chg** - time of the most recent individual OS mismatch (e.g., due to multiboot or IP reuse).
- int: **distance**  - system distance (derived from TTL; -1 if no data).
- int: **bad_sw**    - p0f thinks the User-Agent or Server strings aren't accurate. The value of 1 means OS difference (possibly due to proxying), while 2 means an outright mismatch. NOTE: If User-Agent is not present at all, this value stays at 0.
- int: **os_match_q** - OS match quality: 0 for a normal match; 1 for fuzzy (e.g., TTL or DF difference); 2 for a generic signature; and 3 for both.
- string: **os_name** - Name of the most recent positively matched OS. If OS not known, os_name is empty string. NOTE: If the host is first seen using an known system and then switches to an unknown one, this field is not reset.
- string: **os_flavor**   - OS version. May be empty if no data.
- string: **http_name**   - most recent positively identified HTTP application (e.g. 'Firefox').
- string: **http_flavor** - version of the HTTP application, if any.
- string: **link_type**   - network link type, if recognized.
- string: **language**    - system language, if recognized.
