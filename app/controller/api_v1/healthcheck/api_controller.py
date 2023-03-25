from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/health-check")
def check_server_health():
    return Response("OK")
