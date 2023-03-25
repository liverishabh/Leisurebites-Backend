import json
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from app.dependencies.logger import ApplicationLogger

logger = ApplicationLogger.get_logger(__name__)


class RequestResponseLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            logger.info(f"{request.method} {request.url.path}?{request.url.query}")
            req_body = await request.body()
            if req_body:
                # req_json = json.loads(req_body.decode("utf-8"))
                # logger.info(f"Request Body: {json.dumps(req_json)}")
                try:
                    logger.info(f"Request Body: {req_body.decode('utf-8')}")
                except Exception as ex:
                    pass

            response: Response = await original_route_handler(request)
            resp_json = json.loads(response.body.decode("utf-8"))
            logger.info(f"Response Body: {json.dumps(resp_json)}")
            logger.info(f"Response Status Code: {response.status_code}")

            return response

        return custom_route_handler
