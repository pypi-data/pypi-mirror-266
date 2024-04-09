import logging

import colander
from sqlalchemy import distinct
from sqlalchemy.orm import (
    selectinload,
    joinedload,
)

from caerp.models.indicators import CustomBusinessIndicator
from caerp.models.project.business import Business
from caerp.models.project.types import (
    BusinessType,
)
from caerp.models.task import (
    Task,
    Invoice,
)
from caerp.models.project import Project
from caerp.models.third_party.customer import Customer
from caerp.models.company import Company
from caerp.models.training.bpf import BusinessBPFData

from caerp.forms.business.business import get_business_list_schema

from caerp.utils.widgets import Link
from caerp.views import BaseListView

from caerp.views.business.routes import BUSINESS_ITEM_ROUTE, BUSINESSES_ROUTE
from caerp.views.company.routes import ITEM_ROUTE as COMPANY_ROUTE


logger = logging.getLogger(__name__)


class BusinessListTools:
    schema = get_business_list_schema(is_global=True)

    def query(self):
        query = self.dbsession.query(distinct(Business.id), Business)
        query = query.options(
            joinedload(Business.project)
            .load_only("id")
            .selectinload(Project.company)
            .load_only(Company.id, Company.name),
            selectinload(Business.tasks)
            .selectinload(Project.customers)
            .load_only(Customer.id, Customer.label),
            selectinload(Business.invoices_only).load_only(
                Invoice.financial_year,
            ),
            joinedload(Business.business_type).load_only("id", "bpf_related"),
            selectinload(Business.bpf_datas),
        )
        return query

    def filter_company_id(self, query, appstruct):
        company_id = appstruct.get("company_id", None)
        if company_id not in (None, "", colander.null):
            logger.debug("  + Filtering on company_id")
            query = query.join(Business.project)
            query = query.filter(Project.company_id == company_id)
        return query

    def filter_customer_id(self, query, appstruct):
        customer_id = appstruct.get("customer_id", None)
        if customer_id not in (None, "", colander.null):
            logger.debug("  + Filtering on customer_id")
            query = query.outerjoin(Business.tasks)
            query = query.filter(Business.tasks.any(Task.customer_id == customer_id))
        return query

    def filter_invoicing_year(self, query, appstruct):
        invoicing_year = appstruct.get("invoicing_year", -1)
        if invoicing_year not in (-1, colander.null):
            logger.debug("  + Filtering on invoicing_year")
            query = query.filter(
                Business.invoices_only.any(
                    Invoice.financial_year == invoicing_year,
                )
            )
        return query

    def filter_business_type_id(self, query, appstruct):
        business_type_id = appstruct.get("business_type_id")
        if business_type_id not in ("all", None):
            query = query.filter(Business.business_type_id == business_type_id)
        return query

    def filter_search(self, query, appstruct):
        search = appstruct.get("search", None)

        if search not in (None, colander.null, ""):
            logger.debug("  + Filtering on search")
            query = query.outerjoin(Business.tasks)
            query = query.filter(Project.tasks.any(Task.official_number == search))
        return query

    def filter_include_closed(self, query, appstruct):
        include_closed = appstruct.get("include_closed", False)
        if not include_closed:
            logger.debug("  + Filtering on businesses")
            query = query.filter(Business.closed == False)
        return query

    def filter_bpf_filled(self, query, appstruct):
        """
        Double behaviour :
        -  if a year is selected, check bpf_filled for that given year (see
          filter_invoicing_year)
        -  else check global bpf_filled indicator
        """
        invoicing_year = appstruct.get("invoicing_year", -1)
        bpf_filled = appstruct.get("bpf_filled", None)

        if bpf_filled:
            if bpf_filled == "no":
                query = query.join(Business.business_type)
                query = query.filter(BusinessType.bpf_related == False)
            else:
                if bpf_filled == "yes":
                    query = query.join(Business.business_type)
                    query = query.filter(BusinessType.bpf_related == True)
                if invoicing_year != -1:
                    logger.debug(
                        "  + Filtering on bpf status for year {}".format(invoicing_year)
                    )
                    query.join(BusinessBPFData, isouter=True)
                    year_filter = Business.bpf_datas.any(
                        BusinessBPFData.financial_year == invoicing_year
                    )
                    if bpf_filled == "full":
                        query = query.filter(year_filter)
                    if bpf_filled == "partial":
                        query = query.filter(~year_filter)
                else:
                    logger.debug("  + Filtering on bpf status for all years")
                    query = query.join(CustomBusinessIndicator, isouter=True,).filter(
                        CustomBusinessIndicator.name == "bpf_filled",
                    )

                    if bpf_filled == "full":
                        query = query.filter(
                            CustomBusinessIndicator.status
                            == CustomBusinessIndicator.SUCCESS_STATUS
                        )
                    if bpf_filled == "partial":
                        query = query.filter(
                            CustomBusinessIndicator.status.in_(
                                [
                                    CustomBusinessIndicator.DANGER_STATUS,
                                    CustomBusinessIndicator.WARNING_STATUS,
                                ]
                            )
                        )

        return query


class GlobalBusinessListView(BusinessListTools, BaseListView):
    """
    View listing businesses"

    Status
    Company
    Customers (?)
    CA
    Actions
    """

    is_admin = True
    title = "Liste des affaires de la CAE"
    add_template_vars = ("stream_columns", "stream_actions")

    def stream_columns(self, item):
        yield (
            "<span class='btn btn-{0} icon'>"
            "<svg><use href='static/icons/endi.svg#icon-{0}'></use></svg>"
            "</span>".format(item.status)
        )
        yield item.name
        yield item.project.company.name
        if item.tasks:
            yield item.tasks[0].customer.label
        else:
            yield "Cette affaire est vide"

    def stream_actions(self, item):
        yield Link(
            self.request.route_path(
                BUSINESS_ITEM_ROUTE,
                id=item.id,
            ),
            "Voir l'affaire",
            icon="arrow-right",
            css="icon",
        )
        if item.tasks:
            yield Link(
                self.request.route_path(
                    "customer",
                    id=item.tasks[0].customer.id,
                ),
                "Voir le client {}".format(item.tasks[0].customer.label),
                icon="user",
                css="icon",
            )
        if self.is_admin:
            yield Link(
                self.request.route_path(
                    COMPANY_ROUTE,
                    id=item.project.company.id,
                ),
                "Voir l'enseigne {}".format(item.project.company.name),
                icon="building",
                css="icon",
            )


def includeme(config):
    config.add_view(
        GlobalBusinessListView,
        route_name=BUSINESSES_ROUTE,
        renderer="/business/list_businesses.mako",
        permission="admin.training",
    )
    config.add_admin_menu(
        parent="sale",
        order=0,
        label="Affaires",
        href=BUSINESSES_ROUTE,
    )
