from typing import Union

from fastapi import Request, responses
from fastapi.exceptions import HTTPException, RequestValidationError
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError

from error import AppError


def validation_error(
    request: Request, exec: Union[RequestValidationError, ValidationError]
) -> responses.JSONResponse:
    error = exec.errors()[0]
    field = error.get("loc")[-1]
    message = error.get("msg")

    error_msg = f"invalid {field}: {message}"
    return responses.JSONResponse(status_code=422, content={"message": error_msg})


def validation_for_http_exception(
    request: Request, exec: HTTPException
) -> responses.JSONResponse:
    return responses.JSONResponse(
        status_code=exec.status_code, content={"message": exec.detail}
    )


def validation_for_all_exceptions(
    request: Request, exec: ValueError
) -> responses.JSONResponse:
    return responses.JSONResponse(status_code=400, content={"message": exec.args[0]})


def validation_for_db_errors(
    request: Request, exec: Union[IntegrityError, DBAPIError]
) -> responses.JSONResponse:
    error_msg = exec.args[0]
    if "UNIQUE" in error_msg:
        error_msg = (
            f"{error_msg.split(':')[1].split('.')[1].capitalize()} already exists"
        )
    return responses.JSONResponse(status_code=422, content={"message": error_msg})


def validation_app_error(request: Request, exec: AppError):
    return responses.JSONResponse(
        status_code=exec.status_code, content={"message": exec.message}
    )


def validation_jwt_error(request: Request, exc: JWTError):
    """
    Handle JWT Exceptions.
    """
    return responses.JSONResponse(
        status_code=401,
        content={
            "message": f"Invalid Token {exc}",
        },
    )
