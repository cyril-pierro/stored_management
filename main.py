from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError

import handlers as hlp
from api.v1.routers import operations as op
from api.v1.routers import stock_control_operations as scp
from core.setup import Base, engine
from utils.common import responses

disable_installed_extensions_check()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Store Management System",
    description="Manage Store Stocks with the organization",
    responses=responses,
)
app.include_router(op.op_router, tags=["Management Operations"])
app.include_router(scp.op_router, tags=["Stock Controll Operations"])
add_pagination(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(ValueError, hlp.validation_for_all_exceptions)
app.add_exception_handler(HTTPException, hlp.validation_for_http_exception)
app.add_exception_handler(RequestValidationError, hlp.validation_error)
app.add_exception_handler(ValidationError, hlp.validation_error)
app.add_exception_handler(DBAPIError, hlp.validation_for_db_errors)
app.add_exception_handler(IntegrityError, hlp.validation_for_db_errors)
