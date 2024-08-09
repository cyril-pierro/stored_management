from pydantic import BaseModel


class JobIn(BaseModel):
    name: str


class JobOut(BaseModel):
    id: int
    name: str


class DepartmentIn(JobIn):
    pass


class DepartmentOut(JobOut):
    pass
