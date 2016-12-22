import os
import random

from vaurien.behaviors.error import Error, _ERRORS, random_http_error, _TMP
from vaurien.util import get_data


_ERRORS_EXT = {
    504: ("Gateway Time-out",
          ('<p> The server was acting as a gateway or proxy and did not'
           'receive a timely response from the upstream server.</p>'))
}
_ERRORS_EXT.update(_ERRORS)
_ERROR_CODES = _ERRORS_EXT.keys()


def random_http_error():
    data = {}
    data['code'] = code = random.choice(_ERROR_CODES)
    data['name'], data['description'] = _ERRORS_EXT[code]
    return _TMP % data


class DummyError(Error):
    """Reads the packets that have been sent then send back "errors".

    Used in cunjunction with the HTTP Procotol, it will transfer request to
    the backend and randomly send back a 501, 502, 503 or 504 error.
    """
    name = 'dummy_error'

    def on_before_handle(self, protocol, source, dest, to_backend):
        if self.current < self.option('warmup'):
            self.current += 1
            return super(Error, self).on_before_handle(protocol, source,
                                                       dest, to_backend)

        # read the data
        data = get_data(source)
        if not data:
            return False

        # error out
        if protocol.name == 'http' and to_backend:
            dest.sendall(data)  # send request to backend
            source.sendall(random_http_error())  # but return 5xx error
            source.close()
            source._closed = True
            return False

        return True
