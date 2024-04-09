import datetime
import logging

from dateutil.relativedelta import relativedelta
from typing import Union
from sqlalchemy import (
    distinct,
    func,
)

from caerp_base.models.base import DBSESSION
from caerp.models.accounting.operations import AccountingOperation
from caerp.models.config import Config


logger = logging.getLogger(__name__)


ACCOUNTING_SOFTWARES = [
    (None, "Non défini"),
    ("sage", "SAGE"),
    ("sage_experts", "SAGE GENERATION EXPERTS"),
    ("quadra", "QUADRA / CEGID"),
    ("isacompta", "ISACOMPTA"),
    ("ibiza", "IBIZA"),
    ("ebp", "EBP"),
    ("ciel", "CIEL"),
    ("cador", "CADOR"),
]


def get_accounting_closure_values() -> tuple:
    """
    Return the day and month of the configured accounting closure
    """
    closure_day = Config.get_value("accounting_closure_day", default=31, type_=int)
    closure_month = Config.get_value("accounting_closure_month", default=12, type_=int)
    return closure_day, closure_month


def get_financial_year_data(
    year: Union[int, str] = datetime.date.today().year,
) -> dict:
    """
    Compute usefull data for a given financial year
    according to accounting closure config

    param int|str year : The END'S YEAR of the financial year we want

    :returns: A dict with all usefull data of the financial year
    {
        "label": str = Financial year global label ("yyyy" or "yyyy/yy")
        "start_date": str = Financial year start date ("yyyy-mm-dd")
        "start_year": int = Financial year start year (yyyy)
        "start_month": int = Financial year start month (m)
        "start_label": str = Financial year start label ("dd/mm/yyyy")
        "end_date": str = Financial year end date ("yyyy-mm-dd")
        "end_year": int = Financial year end year (yyyy)
        "end_month": int = Financial year end month (m)
        "end_label": str = Financial year end label ("dd/mm/yyyy")
    }
    """
    closure_day, closure_month = get_accounting_closure_values()
    if isinstance(year, str):
        year = int(year)
    end_date = datetime.date(year, closure_month, closure_day)
    start_date = end_date - relativedelta(years=1) + relativedelta(days=1)
    label = str(start_date.year)
    if end_date.year != start_date.year:
        label += "/{}".format(end_date.strftime("%y"))
    return {
        "label": label,
        "start_date": start_date,
        "start_year": start_date.year,
        "start_month": start_date.month,
        "start_label": start_date.strftime("%d/%m/%Y"),
        "end_date": end_date,
        "end_year": end_date.year,
        "end_month": end_date.month,
        "end_label": end_date.strftime("%d/%m/%Y"),
    }


def get_current_financial_year_data() -> dict:
    """
    Return usefull data on the current financial year
    """
    today = datetime.date.today()
    closure_day, closure_month = get_accounting_closure_values()
    year = today.year
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        year += 1
    return get_financial_year_data(year)


def get_previous_financial_year_data() -> dict:
    """
    Return usefull data on the previous financial year
    """
    today = datetime.date.today()
    closure_day, closure_month = get_accounting_closure_values()
    year = today.year - 1
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        year += 1
    return get_financial_year_data(year)


def get_current_financial_year_value() -> int:
    """
    Return the year value (end's year) of the current financial year
    """
    today = datetime.date.today()
    current_financial_year = today.year
    closure_day, closure_month = get_accounting_closure_values()
    if today.month > closure_month or (
        today.month == closure_month and today.day > closure_day
    ):
        current_financial_year += 1
    return current_financial_year


def get_all_financial_year_values() -> list:
    """
    Return the year values (end's year) of the known financial years
    """
    query = DBSESSION().query(distinct(func.extract("YEAR", AccountingOperation.date)))
    query = query.order_by(AccountingOperation.date.desc())
    years = [year[0] for year in query]
    if get_current_financial_year_value() not in years:
        years.insert(0, get_current_financial_year_value())
    return years


def get_cae_accounting_software() -> (str, str):
    """
    Return id and label of configured CAE's accounting software
    """
    cae_accounting_software = Config.get_value("accounting_software")
    for software_id, software_label in ACCOUNTING_SOFTWARES:
        if software_id == cae_accounting_software:
            return (software_id, software_label)
    return ACCOUNTING_SOFTWARES[0]
