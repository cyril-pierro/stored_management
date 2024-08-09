from fastapi import APIRouter

from controllers.operations import (DepartmentOperator, JobOperator,
                                    StaffOperator)
from schemas.operations import DepartmentIn, JobIn
from schemas.staff import StaffIn, UpdateStaffIn

op_router = APIRouter()


@op_router.get("/staff")
def get_staff_members():
    return StaffOperator.get_all_staff_members()


@op_router.get("/staff/{id}")
def get_staff_member(id: int):
    staff = StaffOperator.get_staff(id)
    if not staff:
        raise ValueError("No staff found")
    return staff.json()


@op_router.post("/staff")
def add_staff_member(data: StaffIn):
    return StaffOperator.create_staff(data).json()


@op_router.delete("/staff/{id}")
def remove_staff_member(id: int):
    return StaffOperator.delete_staff_by_id(id)


@op_router.put("/staff/{id}")
def update_staff_member(id: int, data: UpdateStaffIn):
    return StaffOperator.update_staff_by_id(id, data).json()


@op_router.get("/job-titles")
def get_all_job_titles():
    return JobOperator.get_all_job_titles()


@op_router.post("/job-title")
def add_job_title(data: JobIn):
    return JobOperator.create_job_title(data).json()


@op_router.get("/job-title/{id}")
def get_job_title(id: int):
    job = JobOperator.get_job_title(id)
    if not job:
        raise ValueError("Job not found")
    return job.json()


@op_router.put("/job-title/{id}")
def edit_job_title(id: int):
    return JobOperator.edit_job_title(id).json()


@op_router.delete("/job-title/{id}")
def delete_job_title(id: int):
    return JobOperator.delete_job_title(id)


@op_router.get("/department")
def get_departments():
    return DepartmentOperator.get_all_departments()


@op_router.post("/department")
def add_department(data: DepartmentIn):
    return DepartmentOperator.create_department(data).json()


@op_router.get("/department/{id}")
def get_department(id: int):
    dep_found = DepartmentOperator.get_department(id)
    if not dep_found:
        raise ValueError("No department found")
    return dep_found.json()


@op_router.delete("/department/{id}")
def delete_department(id: int):
    return DepartmentOperator.delete_department(id)


@op_router.put("/department/{id}")
def update_department(id: int, data: DepartmentIn):
    return DepartmentOperator.edit_department(id, data.name).json()
