import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError

import handlers as hlp
from api.v1.routers import (
    auth,
    engineer as cu,
    operations as op,
    stock_control as scp,
    report,
    purchase_order
)
from core.setup import Base, engine
from error import AppError
from utils.common import responses

disable_installed_extensions_check()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Store Management System",
    description="Manage Store Stocks with the organization",
    responses=responses,
)
app.include_router(op.op_router, tags=["Management Operations"])
app.include_router(scp.op_router, tags=["Stock Control Operations"])
app.include_router(cu.op_router, tags=["Engineer Operations"])
app.include_router(purchase_order.po_router, tags=["Purchase Order Operations"])
app.include_router(auth.op_router, tags=["Authentication Operations"])
app.include_router(report.op_router, tags=["Stock Reports"])

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
app.add_exception_handler(AppError, hlp.validation_app_error)
app.add_exception_handler(JWTError, hlp.validation_jwt_error)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
