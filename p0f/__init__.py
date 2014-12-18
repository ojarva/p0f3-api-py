"""
The MIT License (MIT)

Copyright (c) 2014 Olli Jarva <olli@jarva.fi>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


import struct
import socket
import datetime

class P0f:
    """ This class is used to query data from p0f3, available from
        http://lcamtuf.coredump.cx/p0f3/

        This is not compatible with version 1.x or 2.x of p0f.

        Start p0f3 with "-s name" option (e.g "-s p0f.sock"). Do note
        p0f3 restricts the number of simultaneous API connections.
        You have to either delete instance of this class or run
        .close() to disconnect. New connection is automatically
        opened when running get_info()


            p0f = P0f("p0f.sock")
            data = p0f.get_info("192.168.2.1")
            p0f.close()
    """
    RESPONSE_FIELDS = ["magic", "status", "first_seen", "last_seen",
             "total_conn", "uptime_min", "up_mod_days", "last_nat",
             "last_chg", "distance", "bad_sw", "os_match_q", "os_name",
             "os_flavor", "http_name", "http_flavor", "link_type", "language"]
    RESPONSE_FMT = "IbIIIIIIIhbb32s32s32s32s32s32s"

    RESPONSE_NO_MATCH = 32
    RESPONSE_OK = 16
    RESPONSE_BAD_QUERY = 0

    RESPONSE_STATUS = {32: RESPONSE_NO_MATCH,
                       16: RESPONSE_OK,
                        0: RESPONSE_BAD_QUERY}

    RESPONSE_DATETIME_PARSE = ["first_seen", "last_seen", "last_nat", 
                               "last_chg"]


    OS_MATCH_NORMAL = 0
    OS_MATCH_FUZZY = 1
    OS_MATCH_GENERIC = 2
    OS_MATCH_BOTH = 3

    RESPONSE_OS_MATCH = {0: OS_MATCH_NORMAL,
                         1: OS_MATCH_FUZZY,
                         2: OS_MATCH_GENERIC,
                         3: OS_MATCH_BOTH}

    BAD_SW_NA = 0
    BAD_SW_OS_MISMATCH = 1
    BAD_SW_MISMATCH = 2

    RESPONSE_BAD_SW = {0: BAD_SW_NA,
                       1: BAD_SW_OS_MISMATCH,
                       2: BAD_SW_MISMATCH}

    def __init__(self, socket_path, **kwargs):
        self.socket_path = socket_path
        self._client = None
        self.timeout = kwargs.get("timeout", 0.1)

    @property
    def client(self):
        """ Returns (cached) socket connection to p0f """
        if not self._client:
            self._client = socket.socket(socket.AF_UNIX)
            self._client.settimeout(self.timeout)
            self._client.connect(self.socket_path)
        return self._client

    def close(self):
        """ Closes (cached) socket connection """
        if not self._client:
            return
        self._client.close()

    def get_info(self, ip_address, return_raw_data=False):
        """ Returns information retrieved from p0f.
            Raises
               P0fException for invalid queries
               KeyError if no data is available
               socket.error if socket is disconnected
               ValueError if invalid constant value is
                          returned.

            Returns dictionary matching to fields defined in
                http://lcamtuf.coredump.cx/p0f3/README
            under "API access".
        """

        address_class = socket.AF_INET
        if ":" in ip_address:
            address_class = socket.AF_INET6
        packed_address = socket.inet_pton(address_class, ip_address)
        data_send = struct.pack("Ib", 0x50304601, 4) + packed_address
        if address_class == socket.AF_INET:
            data_send += struct.pack("12x")
        self.client.send(data_send)
        data_received = self.client.recv(1024)
        values = struct.unpack(self.RESPONSE_FMT, data_received)

        data_in = {}
        for i in range(len(values)):
            value = values[i]
            if isinstance(value, str):
                value = value.replace("\x00", "")
            data_in[self.RESPONSE_FIELDS[i]] = value

        if data_in["magic"] != 0x50304602:
            raise P0fException("Server returned invalid magic number")

        status = self.RESPONSE_STATUS[data_in["status"]]
        if status == self.RESPONSE_BAD_QUERY:
            raise P0fException("Improperly formatted query sent to p0f")
        elif status == self.RESPONSE_NO_MATCH:
            raise KeyError("No data available in p0f for %s" % ip_address)
        if return_raw_data:
            return data_in

        return P0f.format_data(data_in)

    @classmethod
    def format_data(cls, data_in):
        """ Parses p0f response to datetime, validates constants and
            replaces empty values with None """
        for field in cls.RESPONSE_DATETIME_PARSE:
            if data_in[field] == 0:
                data_in[field] = None
                continue
            data_in[field] = datetime.datetime.fromtimestamp(data_in[field])
        data_in["up_mod_days"] = datetime.timedelta(days=data_in["up_mod_days"])

        if data_in["uptime_min"] == 0:
            data_in["uptime"] = None
            data_in["uptime_min"] = None
            data_in["uptime_sec"] = None
        else:
            data_in["uptime_sec"] = data_in["uptime_min"] * 60
            data_in["uptime"] = datetime.timedelta(seconds=data_in["uptime_sec"])

        if data_in["os_match_q"] not in cls.RESPONSE_OS_MATCH:
            raise ValueError("p0f provided invalid value for os_match_q: %s"
                               % data_in["os_match_q"])
        if data_in["bad_sw"] not in cls.RESPONSE_BAD_SW:
            raise ValueError("p0f responded with invalid bad_sw: %s"
                               % data_in["bad_sw"])

        if data_in["distance"] == -1:
            data_in["distance"] = None
        
        for field in ("up_mod_days", "last_nat", "last_chg", "bad_sw"):
            if data_in[field] == 0:
                data_in[field] = None

        for field in ("os_name", "os_flavor", "http_flavor", "link_type",
                      "language"):
            if len(data_in[field]) == 0:
                data_in[field] = None

        return data_in

class P0fException(Exception):
    """ Raised when server returns invalid data """
    pass

def main():
    """ This is a testing method, executed when
        this file is executed instead of imported. """
    p0f_client = P0f("p0f.sock")
    print(p0f_client.get_info("10.1.0.2"))


if __name__ == '__main__':
    main()
