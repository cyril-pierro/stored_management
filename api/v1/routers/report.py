from fastapi import APIRouter, Depends

from controllers.auth import Auth
from controllers.operations import StaffOperator
from error import AppError
from utils.common import bearer_schema
from controllers.report import ReportDashboard
from schemas.report import ErmReportOut


PERMISSION_ERROR = "You do not have permission to perform this operation"
op_router = APIRouter()


@op_router.get("/reports")
def get_stock_reports(access_token: str = Depends(bearer_schema)):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    data = {
        "department_engineer": ReportDashboard.get_number_of_engineers_in_each_department(),
        "department_adjustment_order": ReportDashboard.get_department_adjustment_order(),
        "department_number_quantity_order": ReportDashboard.get_number_and_quantity_orders_each_department(),
    }
    return data


@op_router.get(
        "/erm",
        # response_model=list[ErmReportOut]
    )
def get_erm_report(
    # access_token: str = Depends(bearer_schema)
):
    # staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    # if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
    #     raise AppError(message=PERMISSION_ERROR, status_code=401)
    return ReportDashboard.get_erm_report_data()
