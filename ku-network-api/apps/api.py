from ninja import NinjaAPI, Schema
from ninja.responses import Response
from ninja.errors import ValidationError, AuthenticationError
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from apps.users.auth import *
from apps.common.exceptions import (
    ErrorCode,
    RequestError,
    request_errors,
    validation_errors,
)
from apps.users.views import auth_router
from django.urls import path


api = NinjaAPI(
    title="KuNetwork API",
    description="""
      A robust, production-grade Crypto Mining API built with Django Ninja
    """,
    version="1.0.0",
    docs_url="/",
    throttle=[AnonRateThrottle("5000/m"), AuthRateThrottle("10000/m")],
)


api.add_router("api/v1/auth", auth_routher)


class HealthCheckResponse(Schema):
    message: str


@api.get("/api/v1/healthcheck/", response=HealthCheckResponse, tags=["HealthCheck (1)"])
async def healthcheck(request):
    return {"message": "pong"}


@api.exception_handler(RequestError)
def request_exc_handler(request, exc):
    return request_errors(exc)


@api.exception_handler(ValidationError)
def validate_exc_handler(request, exc):
    return validation_errors(exc)


@api.exception_handler(AuthenticationError)
def request_exc_handler(request, exc):
    return Response(
        {
            "status": "failure",
            "code": ErrorCode.INVALID_AUTH,
            "message": "Unauthorized User",
        },
        status=401,
    )
