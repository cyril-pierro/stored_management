from typing import Union

from models.department import Department
from models.job import Job
from models.staff import Staff
from schemas.operations import JobIn
from schemas.staff import StaffIn, UpdateStaffIn
from utils.session import DBSession


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
            db.delete(job_found)
            db.commit()
        return True

    @staticmethod
    def edit_job_title(name: str):
        job_found = JobOperator.get_job_title(id)
        if not job_found:
            raise ValueError("Job not found")
        with DBSession() as db:
            job_found.name = name
            db.add(job_found)
            db.commit()
            db.refresh(job_found)
            return job_found


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
            db.delete(dep_found)
            db.commit()
        return True

    @staticmethod
    def edit_department(id: int, name: str) -> Department:
        dep_found = DepartmentOperator.get_department(id)
        if not dep_found:
            raise ValueError("Department not found")
        with DBSession() as db:
            dep_found.name = name
            db.add(dep_found)
            db.commit()
            return db.refresh(dep_found)


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

        new_staff = Staff(
            id=data.id,
            name=data.name,
            job_id=data.job_id,
            department_id=data.department_id,
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
        return staff.save()

    @staticmethod
    def delete_staff_by_id(staff_id: int) -> bool:
        staff = StaffOperator.get_staff(staff_id)
        if not staff:
            raise ValueError("Staff not found")
        with DBSession() as db:
            db.delete(staff)
            db.commit()
        return True

    @staticmethod
    def get_all_staff_members() -> list[Staff]:
        with DBSession() as db:
            return db.query(Staff).all()
