from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from config.setting import settings
from controllers.operations import StaffOperator
from error import AppError
from schemas.staff import ChangePasswordIn, LoginIn
from utils.redis import Cache


class Auth:
    @staticmethod
    def login(data: LoginIn):
        staff = StaffOperator.validate_staff_credentials(data)
        access_token, expires_in = Auth.generate_access_token(
            staff_id=staff.id, for_="login", expires_in_time=1440
        )
        return {"access_token": access_token, "expires_in": expires_in, "data": staff}

    @staticmethod
    def verify_token(token: str, for_) -> bool:
        staff_data = Auth.decode_token(token)
        staff_id = staff_data.get("id")
        value = Cache.get(f"{for_}_{staff_id}")
        if not value:
            raise AppError(message="Token has expired", status_code=403)
        return staff_id

    @staticmethod
    def change_password(staff_id: int, data: ChangePasswordIn):
        status = StaffOperator.change_staff_password(staff_id, data)
        if status:
            return {"message": "Password has been changed"}

    @staticmethod
    def generate_access_token(
        staff_id: int,
        for_: str,
        expires_in_time: int = settings.APP_SECRET_KEY_EXPIRES_IN,
    ) -> tuple[str, Any]:
        created_at = datetime.now(timezone.utc)
        expires_in = created_at + timedelta(minutes=expires_in_time)
        data = {"id": staff_id, "exp": expires_in, "iat": created_at}
        access_token = jwt.encode(data, settings.APP_SECRET_KEY)
        Cache.set(
            key=f"{for_}_{staff_id}",
            value=access_token,
            ex=timedelta(minutes=expires_in_time),
        )
        return access_token, expires_in_time

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, settings.APP_SECRET_KEY)
        except JWTError as e:
            raise JWTError(e) from e
