"""HTTP interface for the calculator used by the deployment exercise."""
import json
import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from app.calculator import add, subtract, multiply, divide

OPERATIONS = {"add": add, "subtract": subtract, "multiply": multiply, "divide": divide}


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path)
        if route.path == "/health":
            self.respond(200, {"status": "healthy"})
        elif route.path == "/calculate":
            try:
                params = parse_qs(route.query)
                operation = params["operation"][0]
                if operation not in OPERATIONS:
                    raise ValueError("Unknown operation")
                a, b = float(params["a"][0]), float(params["b"][0])
                if not math.isfinite(a) or not math.isfinite(b):
                    raise ValueError("Operands must be finite numbers")
                result = OPERATIONS[operation](a, b)
                if not math.isfinite(result):
                    raise ValueError("Result is outside the supported numeric range")
                self.respond(200, {"operation": operation, "result": result})
            except (KeyError, ValueError) as error:
                self.respond(400, {"error": str(error)})
        else:
            self.respond(404, {"error": "Not found"})

    def respond(self, status, payload):
        body = json.dumps(payload, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), CalculatorHandler).serve_forever()
