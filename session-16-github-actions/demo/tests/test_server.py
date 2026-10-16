import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from app.server import CalculatorHandler


@pytest.fixture(scope="module")
def server_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), CalculatorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def test_health(server_url):
    with urlopen(server_url + "/health", timeout=5) as response:
        assert response.status == 200
        assert json.load(response) == {"status": "healthy"}


@pytest.mark.parametrize("operation,a,b,result", [
    ("add", 10, 5, 15), ("subtract", 10, 5, 5),
    ("multiply", 10, 5, 50), ("divide", 10, 5, 2),
])
def test_calculation(server_url, operation, a, b, result):
    with urlopen(f"{server_url}/calculate?operation={operation}&a={a}&b={b}", timeout=5) as response:
        assert response.status == 200
        assert json.load(response)["result"] == result


@pytest.mark.parametrize("path,status", [
    ("/calculate?operation=divide&a=1&b=0", 400),
    ("/calculate?operation=unknown&a=1&b=2", 400),
    ("/calculate?operation=add&a=NaN&b=2", 400),
    ("/calculate?operation=add&a=1", 400),
    ("/missing", 404),
])
def test_invalid_requests(server_url, path, status):
    with pytest.raises(HTTPError) as error:
        urlopen(server_url + path, timeout=5)
    assert error.value.code == status
    assert "error" in json.load(error.value)
