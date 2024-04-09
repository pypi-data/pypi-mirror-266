import logging

from caerp.models.task import Task
from caerp.forms.tasks.invoice import get_list_schema
from caerp.views import TreeMixin
from caerp.views.company.routes import COMPANY_INVOICE_ADD_ROUTE
from caerp.views.invoices.lists import (
    CompanyInvoicesListView,
    CompanyInvoicesCsvView,
    CompanyInvoicesXlsView,
    CompanyInvoicesOdsView,
    filter_all_status,
)
from .routes import (
    CUSTOMER_ITEM_INVOICE_ROUTE,
    CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
)
from .lists import CustomersListView

logger = logging.getLogger(__name__)


class CustomerInvoiceListView(CompanyInvoicesListView, TreeMixin):
    """
    Invoice list for one given Customer
    """

    route_name = CUSTOMER_ITEM_INVOICE_ROUTE
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "financial_year",
            "customer",
        ),
    )
    add_template_vars = CompanyInvoicesListView.add_template_vars + ("add_url",)
    is_admin = False

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_INVOICE_ADD_ROUTE,
            id=self.context.company_id,
            _query={"customer_id": self.context.id},
        )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    @property
    def title(self):
        return "Factures du client {0}".format(self.context.label)

    def filter_customer(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Task.customer_id == self.context.id)
        return query


class CustomerInvoicesCsvView(CompanyInvoicesCsvView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


class CustomerInvoicesXlsView(CompanyInvoicesXlsView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


class CustomerInvoicesOdsView(CompanyInvoicesOdsView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.company_id

    def filter_customer(self, query, appstruct):
        logger.debug(" + Filtering by customer_id")
        return query.filter(Task.customer_id == self.context.id)

    filter_status = filter_all_status


def includeme(config):
    config.add_tree_view(
        CustomerInvoiceListView,
        parent=CustomersListView,
        renderer="customers/invoices.mako",
        permission="list.invoices",
        layout="customer",
    )
    config.add_view(
        CustomerInvoicesCsvView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=csv",
        permission="list.invoices",
    )

    config.add_view(
        CustomerInvoicesOdsView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=ods",
        permission="list.invoices",
    )

    config.add_view(
        CustomerInvoicesXlsView,
        route_name=CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=xls",
        permission="list.invoices",
    )
