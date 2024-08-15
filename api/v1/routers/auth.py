from fastapi import APIRouter, Depends

from controllers.auth import Auth
from schemas.operations import SuccessOut
from schemas.staff import ChangePasswordIn, LoginIn, LoginOut
from utils.common import bearer_schema

op_router = APIRouter()


@op_router.post("/login", response_model=LoginOut)
async def login_staff(data: LoginIn):
    return Auth.login(data)


@op_router.post("/change-password", response_model=SuccessOut)
async def change_staff_password(
    data: ChangePasswordIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    return Auth.change_password(staff_id=staff_id, data=data)
