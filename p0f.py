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
    RESPONSE_STATUS = {32: "No match", 0: "Bad query", 16: "OK"}

    def __init__(self, socket_path):
        self.socket_path = socket_path
        self._client = None

    @property
    def client(self):
        """ Returns (cached) socket connection to p0f """
        if not self._client:
            self._client = socket.socket(socket.AF_UNIX)
            self._client.connect(self.socket_path)
        return self._client

    def close(self):
        """ Closes (cached) socket connection """
        if not self._client:
            return
        self._client.close()

    def get_info(self, ip_address):
        """ Returns information retrieved from p0f.
            Raises
               P0fException for invalid queries
               KeyError if no data is available
               socket.error if socket is disconnected

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
            s = values[i]
            if isinstance(s, str):
                s = s.replace("\x00", "")
            data_in[self.RESPONSE_FIELDS[i]] = s

        status = self.RESPONSE_STATUS[data_in["status"]]
        if status == "Bad query":
            raise P0fException("Improperly formatted query sent to p0f")
        elif status == "No match":
            raise KeyError("No data available in p0f for %s" % ip_address)
        return data_in

class P0fException(Exception):
    pass


if __name__ == '__main__':
    p0f = P0f("p0f.sock")
    p0f.get_info("10.1.7.2")
