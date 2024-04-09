import logging

import colander
from sqlalchemy import distinct
from sqlalchemy.orm import (
    selectinload,
    joinedload,
)

from caerp.models.indicators import CustomBusinessIndicator
from caerp.models.user.user import User
from caerp.models.project.types import (
    BusinessType,
)
from caerp.models.project.business import Business
from caerp.models.task import (
    Task,
    Invoice,
)
from caerp.models.project import Project
from caerp.models.third_party.customer import Customer
from caerp.models.company import Company
from caerp.models.training.bpf import BusinessBPFData

from caerp.forms.training.trainer import get_list_schema
from caerp.forms.training.training import get_training_list_schema

from caerp.views.user.lists import BaseUserListView
from caerp.views.training.routes import TRAINER_LIST_URL


logger = logging.getLogger(__name__)


class TrainerListView(BaseUserListView):
    """
    View listing Trainers
    """

    title = "Liste des formateurs de la CAE (qui ont une fiche formateur)"
    schema = get_list_schema()

    def filter_trainer(self, query, appstruct):
        query = query.join(User.trainerdatas)
        return query


class TrainingListTools:
    schema = get_training_list_schema(is_global=True)

    def _get_training_business_type(self):
        """
        Retrieve the training project type id from the database
        """
        return (
            self.dbsession.query(BusinessType.id).filter_by(name="training").scalar()
            or -1
        )

    def query(self):
        business_type_id = self._get_training_business_type()
        query = self.dbsession.query(distinct(Business.id), Business).filter(
            Business.business_type_id == business_type_id
        )
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
            query = query.filter(Business.closed == False)  # noqa E712
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
            if invoicing_year != -1:
                logger.debug(
                    "  + Filtering on bpf status for year {}".format(invoicing_year)
                )
                query.join(BusinessBPFData, isouter=True)
                year_filter = Business.bpf_datas.any(
                    BusinessBPFData.financial_year == invoicing_year
                )
                if bpf_filled == "yes":
                    query = query.filter(year_filter)
                else:  # no
                    query = query.filter(~year_filter)
            else:
                logger.debug("  + Filtering on bpf status for all years")
                query = query.join(CustomBusinessIndicator, isouter=True,).filter(
                    CustomBusinessIndicator.name == "bpf_filled",
                )

                if bpf_filled == "yes":
                    query = query.filter(
                        CustomBusinessIndicator.status
                        == CustomBusinessIndicator.SUCCESS_STATUS
                    )
                else:  # no
                    query = query.filter(
                        CustomBusinessIndicator.status.in_(
                            [
                                CustomBusinessIndicator.DANGER_STATUS,
                                CustomBusinessIndicator.WARNING_STATUS,
                            ]
                        )
                    )

        return query


def includeme(config):
    config.add_view(
        TrainerListView,
        route_name=TRAINER_LIST_URL,
        renderer="/training/list_trainers.mako",
        permission="visit",
    )
