from datetime import timedelta
from typing import Union

import error as err
from models.department import Department
from models.job import Job
from models.roles import Roles
from models.staff import Staff
from schemas.operations import JobIn
from schemas.staff import ChangePasswordIn, LoginIn, StaffIn, UpdateStaffIn
from utils.enum import RolesStatus
from utils.redis import Cache
from utils.session import DBSession

INVALID_CRED = "Invalid Credentials"


class JobOperator:
    @staticmethod
    def create_job_title(data: JobIn):
        if JobOperator.get_job_title(data.name):
            raise ValueError("Job title already exists")
        new_job = Job(name=data.name)
        return new_job.save()

    @staticmethod
    def get_job_title(name_or_id: Union[str, int]) -> Union[None, Job]:
        with DBSession() as db:
            if isinstance(name_or_id, int):
                found_job = db.query(Job).filter(Job.id == name_or_id).first()
            else:
                found_job = db.query(Job).filter(Job.name == name_or_id).first()
        return found_job

    @staticmethod
    def get_all_job_titles():
        with DBSession() as db:
            return db.query(Job).all()

    @staticmethod
    def delete_job_title(id: int):
        job_found = JobOperator.get_job_title(id)
        if not job_found:
            raise ValueError("Job not found")
        with DBSession() as db:
            job_found = db.merge(job_found)
            db.delete(job_found)
            db.commit()
        return True

    @staticmethod
    def edit_job_title(id: int, name: str):
        job_found = JobOperator.get_job_title(id)
        if not job_found:
            raise ValueError("Job not found")
        job_found.name = name
        return job_found.save(merge=True)


class DepartmentOperator:
    @staticmethod
    def create_department(data: JobIn):
        if DepartmentOperator.get_department(data.name):
            raise ValueError("Department Name already exists")
        new_department = Department(name=data.name)
        return new_department.save()

    @staticmethod
    def get_all_departments():
        with DBSession() as db:
            return db.query(Department).all()

    @staticmethod
    def get_department(name_or_id: Union[str, int]):
        with DBSession() as db:
            if isinstance(name_or_id, int):
                found_department = (
                    db.query(Department).filter(Department.id == name_or_id).first()
                )
            else:
                found_department = (
                    db.query(Department).filter(Department.name == name_or_id).first()
                )
            return found_department

    @staticmethod
    def delete_department(id: int):
        dep_found = DepartmentOperator.get_department(id)
        if not dep_found:
            raise ValueError("Department not found")
        with DBSession() as db:
            dep_found = db.merge(dep_found)
            db.delete(dep_found)
            db.commit()
        return True

    @staticmethod
    def edit_department(id: int, name: str) -> Department:
        dep_found = DepartmentOperator.get_department(id)
        if not dep_found:
            raise ValueError("Department not found")
        dep_found.name = name
        return dep_found.save(merge=True)


class StaffOperator:
    @staticmethod
    def create_staff(data: StaffIn) -> Staff:
        staff_found = StaffOperator.get_staff(data.staff_id_number)
        if staff_found:
            raise ValueError("Staff already exists")
        if not JobOperator.get_job_title(data.job_id):
            raise ValueError("Job Title not Found")
        if not DepartmentOperator.get_department(data.department_id):
            raise ValueError("Department not Found")

        hash_password = Staff.generate_hash_password(data.password)
        new_staff = Staff(
            staff_id_number=data.staff_id_number,
            name=data.name,
            job_id=data.job_id,
            department_id=data.department_id,
            hash_password=hash_password,
            role_id=data.role_id,
        )
        return new_staff.save()

    @staticmethod
    def get_staff(name_or_id: Union[str, int]) -> Union[None, Staff]:
        with DBSession() as db:
            if isinstance(name_or_id, int):
                found_department = (
                    db.query(Staff).filter(Staff.id == name_or_id).first()
                )
            else:
                found_department = (
                    db.query(Staff).filter(Staff.staff_id_number == name_or_id).first()
                )
        return found_department

    @staticmethod
    def update_staff_by_id(staff_id: int, data: UpdateStaffIn) -> Staff:
        staff = StaffOperator.get_staff(staff_id)
        if not staff:
            raise ValueError("Staff not found")
        staff.name = data.name
        staff.role_id = data.role_id
        staff.department_id = data.department_id
        staff.job_id = data.job_id
        return staff.save(merge=True)

    @staticmethod
    def delete_staff_by_id(staff_id: int) -> bool:
        staff = StaffOperator.get_staff(staff_id)
        if not staff:
            raise ValueError("Staff not found")
        with DBSession() as db:
            staff = db.merge(staff)
            db.delete(staff)
            db.commit()
        return True

    @staticmethod
    def get_all_staff_members() -> list[Staff]:
        with DBSession() as db:
            data = db.query(Staff).all()
        return data

    @staticmethod
    def get_all_staff_roles() -> list[Roles]:
        with DBSession() as db:
            data = db.query(Roles).all()
        return data

    @staticmethod
    def validate_staff_credentials(data: LoginIn) -> Staff:
        staff = StaffOperator.get_staff(data.staff_id_number)
        if not staff:
            raise err.AppError(message=INVALID_CRED, status_code=400)
        if not Staff.verify_hash_password(staff.hash_password, data.password):
            set_handler = Cache.get(
                f"handle_number_of_retries_for_{data.staff_id_number}"
            )
            if not set_handler:
                Cache.set(
                    key=f"handle_number_of_retries_for_{data.staff_id_number}",
                    value=1,
                    ex=timedelta(minutes=5),
                )
            else:
                Cache.incr(f"handle_number_of_retries_for_{data.staff_id_number}")
            if (
                int(Cache.get(f"handle_number_of_retries_for_{data.staff_id_number}"))
                > 5
            ):
                raise err.AppError(
                    message="Too many attempts to login, Please try again in 5 minutes",
                    status_code=400,
                )
            raise err.AppError(message=INVALID_CRED, status_code=400)
        return staff

    @staticmethod
    def change_staff_password(staff_id: int, data: ChangePasswordIn) -> bool:
        staff = StaffOperator.get_staff(staff_id)
        if not staff:
            raise err.AppError(message=INVALID_CRED, status_code=400)
        if not Staff.verify_hash_password(staff.hash_password, data.old_password):
            raise err.AppError(message=INVALID_CRED, status_code=400)
        staff.hash_password = Staff.generate_hash_password(data.new_password)
        staff.save(merge=True)
        return True

    @staticmethod
    def has_stock_controller_permission(staff_id: int) -> bool:
        staff_found = StaffOperator.get_staff(staff_id)
        if not staff_found:
            raise err.AppError(
                message="You do not have permission to perform this operation",
                status_code=401,
            )
        return staff_found.roles.name.name == RolesStatus.stock_controller.name

    @staticmethod
    def has_engineer_permission(staff_id: int) -> bool:
        staff_found = StaffOperator.get_staff(staff_id)
        if not staff_found:
            raise err.AppError(
                message="You do not have permission to perform this operation",
                status_code=401,
            )
        return staff_found.roles.name.name == RolesStatus.engineer.name
