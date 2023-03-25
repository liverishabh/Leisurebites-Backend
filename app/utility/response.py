import orjson
from typing import Any

from fastapi import Response


class CustomJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        resp = {"data": content, "successful": True}
        return orjson.dumps(resp)
