import logging
from sqlalchemy.orm import load_only
from caerp.views import BaseRestView
from caerp.views.status.rest_api import StatusLogEntryRestView
from caerp.views.status.utils import get_visibility_options
from caerp.models.company import Company

from .routes import API_ROUTE, API_ITEM_ROUTE

logger = logging.getLogger(__name__)


class CompanyRestView(BaseRestView):
    """Read-only / item-only at the moment"""

    def _jsonify(self, company, fields):
        return dict((field, getattr(company, field)) for field in fields)

    def collection_get(self):
        # Fields est optionnel
        query = Company.query()

        if not self.request.has_permission("admin_companies"):
            fields = ["id", "name"]
        else:
            fields = self.request.params.getall("fields")

        logger.info(fields)
        if fields:
            logger.info("Returning only {}".format(fields))
            query = query.options(load_only(*fields))
        return [self._jsonify(company, fields) for company in query]

    def form_config(self):
        return {"options": {"visibilities": get_visibility_options(self.request)}}


def includeme(config):
    config.add_rest_service(
        factory=CompanyRestView,
        route_name=API_ITEM_ROUTE,
        collection_route_name=API_ROUTE,
        view_rights="view.company",
        add_rights="admin_companies",
        edit_rights="edit_company",
        collection_view_rights="view",
        delete_rights="delete_company",  # delete_company : n'existe pas encore
    )

    config.add_view(
        CompanyRestView,
        attr="form_config",
        route_name="/api/v1/companies/{id}",
        renderer="json",
        request_param="form_config",
        permission="view.company",
    )

    config.add_rest_service(
        StatusLogEntryRestView,
        "/api/v1/companies/{eid}/statuslogentries/{id}",
        collection_route_name="/api/v1/companies/{id}/statuslogentries",
        collection_view_rights="view.company",
        add_rights="view.company",
        view_rights="view.statuslogentry",
        edit_rights="edit.statuslogentry",
        delete_rights="delete.statuslogentry",
    )
