from fastapi import APIRouter, Depends

from controllers.auth import Auth
from controllers.operations import (
    DepartmentOperator,
    JobOperator,
    StaffOperator,
    GroupsOperator,
)
from error import AppError
from models.email import Recipients
from models.category import Category
from schemas.operations import (
    DepartmentIn,
    DepartmentOut,
    EmailConfigureIn,
    EmailConfigureOut,
    JobIn,
    JobOut,
    RolesOut,
    SuccessOut,
    CategoryIn,
    CategoryOut,
)
from schemas.staff import StaffIn, StaffOut, UpdateStaffIn, GroupIn, GroupsOut
from utils.common import bearer_schema

PERMISSION_DENIED = "You do not have permission to perform this operation"


def stock_credentials_verification(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )


op_router = APIRouter()


@op_router.get("/staff", response_model=list[StaffOut])
async def get_staff_members(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return StaffOperator.get_all_staff_members()


@op_router.get("/staff/roles", response_model=list[RolesOut])
async def get_staff_roles():
    return StaffOperator.get_all_staff_roles()


@op_router.get("/staff/{id}", response_model=StaffOut)
async def get_staff_member(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_engineer_permission(staff_id):
        staff = StaffOperator.get_staff(id)
        if not staff:
            raise ValueError("No staff found")
        return staff
    raise AppError(
        message=PERMISSION_DENIED,
        status_code=401,
    )


@op_router.post("/staff", response_model=StaffOut)
async def add_staff_member(data: StaffIn, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return StaffOperator.create_staff(data)


@op_router.delete("/staff/{id}", response_model=SuccessOut)
async def remove_staff_member(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    StaffOperator.delete_staff_by_id(id)
    return {"message": "Staff deleted successfully"}


@op_router.put("/staff/{id}", response_model=StaffOut)
async def update_staff_member(
    id: int, data: UpdateStaffIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return StaffOperator.update_staff_by_id(id, data)


@op_router.get("/staff/{id}/assign/{group_id}", response_model=StaffOut)
def assign_staff_with_group_id(
    id: int, group_id: int, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_manager_permission(staff_id):
        return StaffOperator.assign_group_to_staff(staff_id=id, group_id=group_id)
    raise AppError(
        message=PERMISSION_DENIED,
        status_code=401,
    )


@op_router.get("/staff/{id}/revoke", response_model=StaffOut)
def revoke_user_from_any_group(
    id: int, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if StaffOperator.has_stock_controller_permission(
        staff_id=staff_id
    ) or StaffOperator.has_manager_permission(staff_id):
        return StaffOperator.remove_user_from_any_group(staff_id=id)
    raise AppError(
        message=PERMISSION_DENIED,
        status_code=401,
    )


@op_router.get("/groups", response_model=list[GroupsOut])
async def get_all_groups():
    return GroupsOperator.all_groups()


@op_router.get("/groups/{id}", response_model=GroupsOut)
async def get_group_by_id(id: int):
    return GroupsOperator.get_group(id)


@op_router.get("/categories", response_model=list[CategoryOut])
async def get_all_categories(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Category.get_all()


@op_router.post("/categories")
async def create_category(data: CategoryIn, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Category.add(data)


@op_router.put("/categories/{category_id}", response_model=CategoryOut)
async def update_category_by_id(
    category_id: int, data: CategoryIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Category.update(category_id, data)


@op_router.delete("/categories/{category_id}", response_model=SuccessOut)
async def delete_category_by_id(
    category_id: int, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    category_found = Category.get(category_id)
    if not category_found:
        raise AppError(message="Category not found", status_code=404)
    status = category_found.remove(merge=True)
    if status:
        return {"message": "Category deleted successfully"}


@op_router.get("/job-title", response_model=list[JobOut])
async def get_all_job_titles(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return JobOperator.get_all_job_titles()


@op_router.post("/job-title", response_model=JobOut)
async def add_job_title(data: JobIn, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return JobOperator.create_job_title(data).json()


@op_router.get("/job-title/{id}", response_model=JobOut)
async def get_job_title(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    job = JobOperator.get_job_title(id)
    if not job:
        raise ValueError("Job not found")
    return job.json()


@op_router.put("/job-title/{id}", response_model=JobOut)
async def edit_job_title(
    id: int, data: JobIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return JobOperator.edit_job_title(id=id, name=data.name).json()


@op_router.delete("/job-title/{id}", response_model=SuccessOut)
async def delete_job_title(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    JobOperator.delete_job_title(id)
    return {"message": "Job title deleted successfully"}


@op_router.get("/department", response_model=list[DepartmentOut])
async def get_departments(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return DepartmentOperator.get_all_departments()


@op_router.post("/department", response_model=DepartmentOut)
async def add_department(
    data: DepartmentIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return DepartmentOperator.create_department(data).json()


@op_router.get("/department/{id}", response_model=DepartmentOut)
async def get_department(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    dep_found = DepartmentOperator.get_department(id)
    if not dep_found:
        raise ValueError("No department found")
    return dep_found.json()


@op_router.delete("/department/{id}", response_model=SuccessOut)
async def delete_department(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    DepartmentOperator.delete_department(id)
    return {"message": "Department Deleted successfully"}


@op_router.put("/department/{id}", response_model=DepartmentOut)
async def update_department(
    id: int, data: DepartmentIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return DepartmentOperator.edit_department(id, data.name).json()


@op_router.post("/configure/email", response_model=EmailConfigureOut)
async def configure_email_to_receive_emails(
    data: EmailConfigureIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Recipients.create_recipient(data.email)


@op_router.put("/configure/email/{id}", response_model=EmailConfigureOut)
async def change_email(
    id: int, data: EmailConfigureIn, access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Recipients.update_recipient(id, data.email)


@op_router.delete("/configure/email/{id}", response_model=SuccessOut)
async def delete_email(id: int, access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    if Recipients.delete_recipient(id):
        return {"message": "Email deleted successfully"}


@op_router.get("/configure/emails", response_model=list[EmailConfigureOut])
async def get_all_emails_configured(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(
            message=PERMISSION_DENIED,
            status_code=401,
        )
    return Recipients.get_all_recipients()
