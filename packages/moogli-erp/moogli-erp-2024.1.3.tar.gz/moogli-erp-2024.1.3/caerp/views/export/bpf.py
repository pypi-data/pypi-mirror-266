import logging
from io import BytesIO

import py3o.template

from caerp.export.utils import write_file_to_request
from caerp.models.project.business import Business
from caerp.models.project.types import BusinessType
from caerp.models.project.project import Project
from caerp.models.services.bpf import BPFService
from caerp.models.training.bpf import BusinessBPFData
from caerp.views.export.utils import get_bpf_year_form
from caerp.utils.widgets import ViewLink
from caerp.views.export import BaseExportView
from caerp.views.export.routes import BPF_EXPORT_ODS_URL
from caerp.models.task import Invoice
from caerp.views.business.routes import BUSINESSES_ROUTE


logger = logging.getLogger(__name__)

MISSING_BPF_DATA = """
Des données BPF sont manquantes pour l'affaire <a target='_blank'
href='/businesses/{id}/bpf' title="Ce document s’ouvrira dans une nouvelle fenêtre"
aria-label="Ce document s’ouvrira dans une nouvelle fenêtre">{name}
</a>
"""


class BPFExportView(BaseExportView):
    title = "Export du Bilan Pédagogique de Formation (BPF)"

    def _populate_action_menu(self):
        self.request.actionmenu.add(
            ViewLink(
                label="Liste des Formations",
                path=BUSINESSES_ROUTE,
                _query=dict(__formid__="deform", bpf_filled="yes"),
            )
        )

    def before(self):
        self._populate_action_menu()

    def get_forms(self):
        form = get_bpf_year_form(
            self.request,
            title="Export BPF par année",
        )

        return {form.formid: {"form": form, "title": "Export BPF par année"}}

    def query(self, query_params_dict, form_name):
        if form_name != "bpf_main_form":
            raise ValueError("Unknown form")

        year = query_params_dict["year"]
        ignore_missing_data = query_params_dict["ignore_missing_data"]
        company_id = query_params_dict.get("company_id")

        query = Business.query().join(
            Business.business_type,
        )
        if company_id is not None:
            query = query.join(Business.project).filter(
                Project.company_id == company_id
            )

        query = query.filter(
            BusinessType.bpf_related == True,  # noqa: E712
            # have at least an invoice in requested year
            Business.invoices_only.any(
                Invoice.financial_year == year,
            ),
        )

        if ignore_missing_data:
            query = query.filter(
                Business.bpf_datas.any(BusinessBPFData.financial_year == year)
            )

        self._year = year
        self._ignore_missing_data = ignore_missing_data

        return query

    def check(self, query):
        count = query.count()
        title = "Vous vous aprêtez à générer un BPF pour {} formations".format(
            count,
        )
        if count > 0:
            uncomplete_businesses = BPFService.check_businesses_bpf(query, self._year)
            print(uncomplete_businesses)
            errors = [
                MISSING_BPF_DATA.format(
                    id=business.id,
                    name=business.name,
                )
                for business in uncomplete_businesses
            ]
        else:
            errors = ["Aucune formation à exporter"]

        return len(errors) == 0, dict(
            errors=errors,
            title=title,
        )

    def produce_file_and_record(self, items, form_name, appstruct):
        # From Business query to BPFData query
        logger.debug("  + Producing file")
        bpf_data_query = (
            BusinessBPFData.query()
            .join(items.subquery(with_labels=True))
            .filter(
                BusinessBPFData.financial_year == self._year,
            )
        )
        logger.info("-> Done")
        return self.generate_bpf_ods(bpf_data_query, self._year)

    def generate_bpf_ods(self, bpf_data_query, invoicing_year):
        bpf_spec = BPFService.get_spec_from_year(invoicing_year)
        template_context = bpf_spec.build_template_context(bpf_data_query)

        output_buffer = BytesIO()
        py3o_template = py3o.template.Template(
            bpf_spec.ods_template,
            output_buffer,
        )
        dl_file_name = "BPF-{}-de MooGLi-{:%Y%m%d}.ods".format(
            invoicing_year,
            template_context["export_date"],
        )
        py3o_template.render(template_context)
        write_file_to_request(self.request, dl_file_name, output_buffer)
        return self.request.response


def includeme(config):
    config.add_view(
        BPFExportView,
        route_name=BPF_EXPORT_ODS_URL,
        renderer="/export/main.mako",
        permission="admin.training",
    )
    config.add_admin_menu(
        parent="training",
        order=4,
        label="Export BPF",
        href=BPF_EXPORT_ODS_URL,
        permission="admin.training",
    )
