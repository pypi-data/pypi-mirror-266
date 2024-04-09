import logging
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
)

from caerp.models.task import Task
from caerp.forms.tasks.invoice import get_list_schema
from caerp.views import (
    TreeMixin,
    BaseFormView,
)
from caerp.views.invoices.lists import (
    CompanyInvoicesListView,
    CompanyInvoicesCsvView,
    CompanyInvoicesXlsView,
    CompanyInvoicesOdsView,
    filter_all_status,
)
from caerp.views.project.business import ProjectBusinessListView
from caerp.views.business.business import (
    get_invoicing_links,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_INVOICE_ROUTE,
    BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
    BUSINESS_ITEM_INVOICING_ROUTE,
    BUSINESS_ITEM_INVOICING_ALL_ROUTE,
)


logger = logging.getLogger(__name__)


class BusinessInvoicesListView(CompanyInvoicesListView, TreeMixin):
    """
    Invoice list for one given company
    """

    route_name = BUSINESS_ITEM_INVOICE_ROUTE
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "year",
            "financial_year",
            "customer",
        ),
    )
    add_template_vars = CompanyInvoicesListView.add_template_vars + ("add_links",)
    is_admin = False

    @property
    def add_links(self):
        return get_invoicing_links(self.context, self.request)

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    @property
    def title(self):
        return "Factures de l'affaire {0}".format(self.request.context.name)

    def filter_business(self, query, appstruct):
        self.populate_navigation()
        query = query.filter(Task.business_id == self.context.id)
        return query


class BusinessInvoicingView(BaseFormView):
    pass


class BusinessInvoicesCsvView(CompanyInvoicesCsvView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "year",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


class BusinessInvoicesXlsView(CompanyInvoicesXlsView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "year",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


class BusinessInvoicesOdsView(CompanyInvoicesOdsView):
    schema = get_list_schema(
        is_global=False,
        excludes=(
            "company_id",
            "year",
            "financial_year",
        ),
    )

    def _get_company_id(self, appstruct):
        return self.request.context.project.company_id

    def filter_business(self, query, appstruct):
        logger.debug(" + Filtering by business_id")
        return query.filter(Task.business_id == self.context.id)

    filter_status = filter_all_status


def gen_invoice_from_payment_deadline(context, request):
    """
    Generate an invoice based on a payment deadline

    :param obj request: The request object
    :param obj context: The current business
    """
    deadline_id = request.matchdict["deadline_id"]
    deadline = context.find_deadline(deadline_id)
    if not deadline:
        return HTTPNotFound()

    invoices = context.gen_invoices(request, request.identity, [deadline])
    return HTTPFound(
        request.route_path(
            "/invoices/{id}",
            id=invoices[0].id,
        )
    )


def gen_all_invoices(context, request):
    """
    Generate all invoices attached to a business

    :param obj request: The request object
    :param obj context: The current Business
    """
    logger.debug("Generating invoices for the business {}".format(context.id))
    invoices = context.gen_invoices(request, request.identity)
    logger.debug(invoices)
    if len(invoices) == 1:
        return HTTPFound(
            request.route_path(
                "/invoices/{id}",
                id=invoices[0].id,
            )
        )
    else:
        return HTTPFound(
            request.route_path(
                BUSINESS_ITEM_INVOICE_ROUTE,
                id=context.id,
            )
        )


def add_invoice_view(context, request):
    """
    View used to add an invoice to the current business
    """
    invoice = context.add_invoice(request, request.identity)
    return HTTPFound(request.route_path("/invoices/{id}", id=invoice.id))


def includeme(config):
    config.add_tree_view(
        BusinessInvoicesListView,
        parent=ProjectBusinessListView,
        renderer="caerp:templates/business/invoices.mako",
        permission="list.invoices",
        layout="business",
    )
    config.add_view(
        BusinessInvoicesCsvView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=csv",
        permission="list.invoices",
    )

    config.add_view(
        BusinessInvoicesOdsView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=ods",
        permission="list.invoices",
    )

    config.add_view(
        BusinessInvoicesXlsView,
        route_name=BUSINESS_ITEM_INVOICE_EXPORT_ROUTE,
        match_param="extension=xls",
        permission="list.invoices",
    )
    config.add_view(
        gen_invoice_from_payment_deadline,
        route_name=BUSINESS_ITEM_INVOICING_ROUTE,
        permission="add.business_invoice",
    )
    config.add_view(
        gen_all_invoices,
        route_name=BUSINESS_ITEM_INVOICING_ALL_ROUTE,
        permission="add.business_invoice",
    )
    config.add_view(
        add_invoice_view,
        route_name=BUSINESS_ITEM_INVOICE_ROUTE,
        permission="add.business_invoice",
        request_param="action=add",
        layout="default",
    )
