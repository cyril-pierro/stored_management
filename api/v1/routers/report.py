from fastapi import APIRouter, Depends, Query

from controllers.auth import Auth
from controllers.operations import StaffOperator
from error import AppError
from utils.common import bearer_schema
from controllers.report import ReportDashboard
from schemas.report import ErmReportOut
from datetime import datetime
from typing import Optional


PERMISSION_ERROR = "You do not have permission to perform this operation"
op_router = APIRouter()


@op_router.get("/reports")
async def get_stock_reports(access_token: str = Depends(bearer_schema)):
    """
    Fetch stock reports for various departments. This function retrieves data
    related to stock management, including the number of engineers,
    adjustment orders, and quantity orders for each department,
    while ensuring the user has the necessary permissions.

    Args:
        access_token (str, optional): The bearer token used for authentication.
        Defaults to the token provided by the dependency.

    Returns:
        dict: A dictionary containing stock report data for different
        departments.

    Raises:
        AppError: If the user does not have permission to access
        the stock reports.
    """
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=401)
    return {
        "department_engineer": ReportDashboard.get_number_of_engineers_in_each_department(),
        "department_adjustment_order": ReportDashboard.get_department_adjustment_order(),
        "department_number_quantity_order": ReportDashboard.get_number_and_quantity_orders_each_department(),
    }


@op_router.get(
        "/erm",
        response_model=list[ErmReportOut]
    )
def get_erm_report(
    access_token: str = Depends(bearer_schema)
):
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=403)
    return ReportDashboard.get_erm_report_data()


@op_router.get("/analysis/{barcode}")
async def get_analysis_report(
    barcode: str,
    from_: Optional[str] = Query(None),
    to_: Optional[str] = Query(default=str(datetime.now().date())),
    access_token: str = Depends(bearer_schema)
):
    """
    Retrieve an analysis report based on the provided barcode.
    This function serves as an endpoint to fetch analysis
    data associated with a specific barcode.

    Args:
        barcode (str): The barcode for which the analysis report is requested.

    Returns:
        The analysis report data corresponding to the provided barcode.
    """
    staff_id = Auth.verify_token(token=access_token.credentials, for_="login")
    if not StaffOperator.has_stock_controller_permission(staff_id=staff_id):
        raise AppError(message=PERMISSION_ERROR, status_code=403)
    from_datetime = from_
    if from_:
        from_datetime = datetime.strptime(from_, '%Y-%m-%d')
    to_datetime = datetime.strptime(to_, '%Y-%m-%d')
    return ReportDashboard.get_analysis_for_barcode(
        barcode,
        from_datetime,
        to_datetime
    )
