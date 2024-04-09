import colander
import datetime
import logging

from collections import OrderedDict
from sqlalchemy import distinct, desc

from caerp_base.models.base import DBSESSION
from caerp.models.user.user import User
from caerp.models.expense.sheet import ExpenseSheet
from caerp.models.expense.types import (
    ExpenseType,
    ExpenseKmType,
    ExpenseTelType,
)
from caerp.utils.widgets import (
    Link,
    PopUp,
)
from caerp.resources import admin_expense_js
from caerp.forms.expense import (
    get_list_schema,
)
from caerp.views import (
    AsyncJobMixin,
    BaseListView,
)
from caerp.views.expenses.utils import get_payment_form

from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import export_expenses_to_file


logger = logging.getLogger(__name__)


class ExpenseListTools:
    title = "Liste des notes de dépenses de la CAE"
    schema = get_list_schema()
    sort_columns = dict(
        official_number=ExpenseSheet.official_number,
        month=ExpenseSheet.month,
        name=User.lastname,
    )
    default_sort = "month"
    default_direction = "desc"

    def query(self):
        query = DBSESSION().query(distinct(ExpenseSheet.id), ExpenseSheet)
        query = query.outerjoin(ExpenseSheet.user)
        query = query.order_by(ExpenseSheet.year.desc())
        return query

    def filter_search(self, query, appstruct):
        search = appstruct.get("search")
        if search and search != colander.null:
            query = query.filter(ExpenseSheet.official_number == search)
        return query

    def filter_year(self, query, appstruct):
        year = appstruct.get("year")
        if year and year not in (-1, colander.null):
            query = query.filter(ExpenseSheet.year == year)
        return query

    def filter_month(self, query, appstruct):
        month = appstruct.get("month")
        if month and month not in (-1, colander.null, "-1"):
            query = query.filter(ExpenseSheet.month == month)
        return query

    def filter_owner(self, query, appstruct):
        user_id = appstruct.get("owner_id", None)
        if user_id and user_id not in ("", -1, colander.null):
            query = query.filter(ExpenseSheet.user_id == user_id)
        return query

    def filter_status(self, query, appstruct):
        # Must add invalid and notpaid status
        status = appstruct.get("status")
        if status in ("wait", "valid", "invalid"):
            query = query.filter(ExpenseSheet.status == status)
        elif status in ("paid", "resulted"):
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == status)
        elif status == "notpaid":
            query = query.filter(ExpenseSheet.status == "valid")
            query = query.filter(ExpenseSheet.paid_status == "waiting")
        else:
            query = query.filter(ExpenseSheet.status.in_(("valid", "wait")))
        return query

    def filter_doc_status(self, query, appstruct):
        status = appstruct.get("justified_status")
        if status == "notjustified":
            query = query.filter(ExpenseSheet.justified == False)  # noqa
        elif status == "justified":
            query = query.filter(ExpenseSheet.justified == True)  # noqa
        return query


class ExpenseList(ExpenseListTools, BaseListView):
    """
    expenses list

        payment_form

            The payment form is added as a popup and handled through javascript
            to set the expense id
    """

    add_template_vars = (
        "title",
        "payment_formname",
        "stream_main_actions",
        "stream_more_actions",
    )

    @property
    def payment_formname(self):
        """
        Return a payment form name, add the form to the page popups as well
        """
        admin_expense_js.need()
        form_name = "payment_form"
        form = get_payment_form(self.request)
        form.set_appstruct({"come_from": self.request.current_route_path()})
        popup = PopUp(form_name, "Saisir un paiement", form.render())
        self.request.popups[popup.name] = popup
        return form_name

    def more_template_vars(self, response_dict):
        """
        Add template vars to the response dict

        :param obj result: A Sqla Query
        :returns: vars to pass to the template
        :rtype: dict
        """
        ret_dict = BaseListView.more_template_vars(self, response_dict)
        records = response_dict["records"]
        ret_dict["total_ht"] = sum(r[1].total_ht for r in records)
        ret_dict["total_tva"] = sum(r[1].total_tva for r in records)
        ret_dict["total_ttc"] = sum(r[1].total for r in records)
        ret_dict["total_km"] = sum(r[1].total_km for r in records)
        return ret_dict

    def stream_main_actions(self):
        if False:
            yield

    def get_export_path(self, extension, details=False):
        return self.request.route_path(
            "expenses{}_export".format("_details" if details else ""),
            extension=extension,
            _query=self.request.GET,
        )

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="xls"),
            icon="file-excel",
            label="Factures au format Excel",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export excel des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Factures au format ODS",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Factures au format CSV",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des factures de la liste",
        )


def create_global_expenses_export_view(extension):
    class GlobalExpensesView(
        AsyncJobMixin,
        ExpenseListTools,
        BaseListView,
    ):
        model = ExpenseSheet
        filename = "note_depense"

        def _build_return_value(self, schema, appstruct, query):
            """
            Return the streamed file object
            """
            all_ids = [elem[0] for elem in query]
            logger.debug("    + All_ids where collected : {0}".format(all_ids))
            if not all_ids:
                return self.show_error(
                    "Aucune note de dépense ne correspond à cette requête"
                )

            celery_error_resp = self.is_celery_alive()
            if celery_error_resp:
                return celery_error_resp
            else:
                logger.debug("    + In the GlobalExpenseCsvView._build_return_value")
                job_result = self.initialize_job_result(FileGenerationJob)

                logger.debug("    + Delaying the export_to_file task")
                celery_job = export_expenses_to_file.delay(
                    job_result.id, all_ids, self.filename, extension
                )
                return self.redirect_to_job_watch(celery_job, job_result)

    return GlobalExpensesView


def expense_configured():
    """
    Return True if the expenses were already configured
    """
    length = 0
    for factory in (ExpenseType, ExpenseKmType, ExpenseTelType):
        length += factory.query().count()
    return length > 0


def get_expensesheet_years(company):
    """
    List of years an expensesheet has been retrieved for
    """
    query = (
        DBSESSION().query(distinct(ExpenseSheet.year)).filter_by(company_id=company.id)
    )
    years = [data[0] for data in query.order_by(desc(ExpenseSheet.year))]

    today = datetime.date.today()
    if today.year not in years:
        years.insert(0, today.year)
    return years


def get_expensesheet_by_year(company):
    """
    Return expenses stored by year and users for display purpose
    """
    result = OrderedDict()
    for year in get_expensesheet_years(company):
        result[year] = []
        for user in company.employees:
            expenses = [
                exp
                for exp in user.expenses
                if exp.year == year and exp.company_id == company.id
            ]
            result[year].append((user, expenses))

    return result


def company_expenses_view(request):
    """
    View that lists the expenseSheets related to the current company
    """
    title = "Notes de dépenses"
    if not expense_configured():
        return dict(
            title=title,
            conf_msg="La déclaration des notes de dépenses n'est pas encore \
accessible.",
        )

    expense_sheets = get_expensesheet_by_year(request.context)

    return dict(
        title=title,
        expense_sheets=expense_sheets,
        current_year=datetime.date.today().year,
        several_users=len(request.context.employees) > 1,
    )


def add_routes(config):
    config.add_route(
        "company_expenses",
        "/company/{id}/expenses",
        traverse="/companies/{id}",
    )
    config.add_route("expenses_export", "/expenses.{extension}")


def add_views(config):
    config.add_view(
        ExpenseList,
        route_name="expenses",
        permission="admin.expensesheet",
        renderer="expenses/admin_expenses.mako",
    )

    config.add_view(
        company_expenses_view,
        route_name="company_expenses",
        renderer="expenses/expenses.mako",
        permission="list_expenses",
    )

    config.add_view(
        create_global_expenses_export_view("csv"),
        route_name="expenses_export",
        match_param="extension=csv",
        permission="admin.expensesheet",
    )

    config.add_view(
        create_global_expenses_export_view("ods"),
        route_name="expenses_export",
        match_param="extension=ods",
        permission="admin.expensesheet",
    )

    config.add_view(
        create_global_expenses_export_view("xls"),
        route_name="expenses_export",
        match_param="extension=xls",
        permission="admin.expensesheet",
    )


def includeme(config):
    add_routes(config)
    add_views(config)

    config.add_admin_menu(
        parent="sale",
        order=2,
        label="Notes de dépenses",
        href="/expenses",
        permission="admin.expensesheet",
    )
    config.add_company_menu(
        parent="supply",
        order=1,
        label="Notes de dépenses",
        route_name="company_expenses",
        route_id_key="company_id",
        permission="list_expenses",
        routes_prefixes=["/expenses/{id}"],
    )
