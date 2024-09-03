from pydantic import BaseModel, Field

from schemas.operations import DepartmentOut, JobOut, RolesOut


class StaffIn(BaseModel):
    staff_id_number: str = Field(alias="engineer_id")
    name: str
    password: str
    job_id: int
    department_id: int
    role_id: int


class Staff(BaseModel):
    id: int
    staff_id_number: str
    name: str
    job: JobOut
    department: DepartmentOut
    roles: RolesOut

    class Config:
        from_attributes = True


class StaffOut(BaseModel):
    id: int
    name: str
    staff_id_number: str
    job: JobOut
    department: DepartmentOut
    roles: RolesOut

    class Config:
        from_attributes = True


class UpdateStaffIn(BaseModel):
    name: str
    role_id: int


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str


class LoginIn(BaseModel):
    staff_id_number: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    expires_in: int
    data: Staff

    class Config:
        from_attributes = True
