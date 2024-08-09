from typing import Union

from schemas.error import (BadRequestError, ForbiddenError,
                           InternalProcessError, InvalidToken,
                           NotAuthenticatedError, NotFoundError,
                           UnProcessedEntityError)

responses = {
    403: {"model": ForbiddenError},
    401: {"model": NotAuthenticatedError},
    404: {"model": NotFoundError},
    422: {"model": UnProcessedEntityError},
    400: {"model": Union[BadRequestError, InvalidToken]},
    500: {"model": InternalProcessError},
}
