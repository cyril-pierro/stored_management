from pydantic import BaseModel


class BaseError(BaseModel):
    message: str


class InvalidToken(BaseError):
    ...


class ForbiddenError(BaseError):
    ...


class NotFoundError(BaseError):
    ...


class NotAuthenticatedError(BaseError):
    ...


class BadRequestError(BaseError):
    ...


class UnProcessedEntityError(BaseError):
    ...


class InternalProcessError(BaseError):
    ...
