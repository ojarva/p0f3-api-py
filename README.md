p0f Python API client
=====================

This is a simple API client for p0f3, available at 
http://lcamtuf.coredump.cx/p0f3/ . It is not compatible with version 2.x 
or 1.x.

Basic usage:

```python
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
    pass

if data:
    print "First seen:", data["first_seen"]
    print "Last seen:", data["last_seen"]
```

Data fields
-----------

These are shamelessly copied from [here](http://lcamtuf.coredump.cx/p0f3/README):

- int: **first_seen** - unix time (seconds) of first observation of the host.
- int: **last_seen**  - unix time (seconds) of most recent traffic.
- int: **total_conn** - total number of connections seen.
- int: **uptime_min** - calculated system uptime, in minutes. Zero if not known.
- int: **up_mod_days** - uptime wrap-around interval, in days.
- int: **last_nat**    - time of the most recent detection of IP sharing (NAT,
                         load balancing, proxying). Zero if never detected.
- int: **last_chg**    - time of the most recent individual OS mismatch (e.g.,
                         due to multiboot or IP reuse).
- int: **distance**  - system distance (derived from TTL; -1 if no data).
- int: **bad_sw**    - p0f thinks the User-Agent or Server strings aren't
                       accurate. The value of 1 means OS difference (possibly
                       due to proxying), while 2 means an outright mismatch.
                       NOTE: If User-Agent is not present at all, this value
                       stays at 0.
- int: **os_match_q** - OS match quality: 0 for a normal match; 1 for fuzzy
                        (e.g., TTL or DF difference); 2 for a generic signature;
                        and 3 for both.
- string: **os_name** - NUL-terminated name of the most recent positively matched
                        OS. If OS not known, os_name[0] is NUL.
                        NOTE: If the host is first seen using an known system and
                        then switches to an unknown one, this field is not
                        reset.
- string: **os_flavor**   - OS version. May be empty if no data.
- string: **http_name**   - most recent positively identified HTTP application
                            (e.g. 'Firefox').
- string: **http_flavor** - version of the HTTP application, if any.
- string: **link_type**   - network link type, if recognized.
- string: **language**    - system language, if recognized.
