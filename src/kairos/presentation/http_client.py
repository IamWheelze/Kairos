import json
from urllib import request, error
from urllib.parse import urljoin
from kairos.logging import get_logger
from .client_base import PresentationAPIClient


class HTTPPresentationClient(PresentationAPIClient):
    def __init__(self, base_url: str, routes: dict | None = None, headers: dict | None = None, timeout: float = 2.0):
        self.base_url = base_url.rstrip("/") + "/"
        self.routes = routes or {}
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        self.log = get_logger("kairos.presentation.http")

    def send_command(self, command: str, presentation_id=None, *args):
        path = self.routes.get(command)
        if not path:
            return {"ok": False, "error": f"No route configured for command '{command}'"}

        payload = {
            "command": command,
            "presentation_id": presentation_id,
            "args": list(args),
        }

        data = json.dumps(payload).encode("utf-8")
        url = urljoin(self.base_url, path.lstrip("/"))
        req = request.Request(url, data=data, headers=self.headers, method="POST")
        self.log.debug("POST %s payload=%s", url, payload)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                try:
                    result = json.loads(resp_bytes.decode("utf-8"))
                except json.JSONDecodeError:
                    result = {"ok": True, "raw": resp_bytes.decode("utf-8", errors="replace")}
                return result
        except error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            self.log.error("HTTP %s error for %s: %s", e.code, url, body)
            return {"ok": False, "status": e.code, "error": body}
        except Exception as e:  # noqa: BLE001
            self.log.exception("Request failed for %s", url)
            return {"ok": False, "error": str(e)}

