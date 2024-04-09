import logging

from typing import Dict

from pyramid.httpexceptions import HTTPFound
import deform_extensions
from sqlalchemy.orm import load_only
from sqlalchemy import desc, asc
from sqlalchemy.orm import contains_eager


from caerp_celery.models import FileGenerationJob
from caerp_celery.tasks.export import (
    export_to_file,
)

from caerp.forms.supply.supplier_invoice import (
    get_supplier_invoice_add_by_supplier_schema,
    SupplierInvoiceAddByOrdersSchema,
    SupplierPaymentSchema,
    SupplierInvoiceDispatchSchema,
    UserPaymentSchema,
    SetTypesSchema,
)
from caerp.forms.supply.supplier_invoice import get_supplier_invoice_list_schema
from caerp.forms.company import get_default_employee_from_request

from caerp.models.company import Company

from caerp.models.supply import (
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierOrder,
    SupplierInvoiceSupplierPayment,
)
from caerp.models.supply.payment import SupplierInvoiceUserPayment
from caerp.models.third_party.supplier import Supplier
from caerp.resources import (
    dispatch_supplier_invoice_js,
    supplier_invoice_resources,
)
from caerp.utils.widgets import (
    Link,
    POSTButton,
    ViewLink,
)
from caerp.views import (
    BaseAddView,
    BaseListView,
    BaseFormView,
    BaseView,
    DeleteView,
    submit_btn,
    JsAppViewMixin,
    DuplicateView,
    AsyncJobMixin,
    TreeMixin,
)
from caerp.views.files.controller import FileController
from caerp.views.files.views import FileUploadView
from caerp.views.supply.base_views import SupplierDocListTools

from caerp.views.task.utils import get_task_url, get_task_view_type
from caerp.views.supply.utils import get_supplier_doc_url

from .routes import (
    COLLECTION_ROUTE,
    COLLECTION_EXPORT_ROUTE,
    COMPANY_COLLECTION_ROUTE,
    COMPANY_COLLECTION_EXPORT_ROUTE,
    DISPATCH_ROUTE,
    ITEM_ROUTE,
)

logger = logging.getLogger(__name__)


def populate_actionmenu(request):
    return request.actionmenu.add(
        ViewLink(
            "Revenir à la liste des factures fournisseur",
            path=COMPANY_COLLECTION_ROUTE,
            id=request.context.get_company_id(),
        )
    )


class BaseSupplierInvoiceAddMixin(BaseFormView):
    add_template_vars = ("title",)
    title = "Saisir une facture fournisseur"

    buttons = (submit_btn,)


class SupplierInvoiceAddView(BaseSupplierInvoiceAddMixin, BaseFormView):
    """
    Can lead (redirect) to SupplierInvoice Creation or to supplier selection.
    """

    schema = SupplierInvoiceAddByOrdersSchema()

    def submit_success(self, appstruct):
        company = self.context

        supplier_orders_ids = list(appstruct.pop("supplier_orders_ids", set()))
        if len(supplier_orders_ids) > 0:
            first_order = SupplierOrder.get(supplier_orders_ids[0])
            supplier = Supplier.get(first_order.supplier_id)
            obj = SupplierInvoice(
                supplier_id=supplier.id,
                company_id=company.id,
                payer=get_default_employee_from_request(self.request),
            )
            self.dbsession.add(obj)

            for order_id in supplier_orders_ids:
                order = SupplierOrder.get(order_id)
                order.supplier_invoice = obj
                self.dbsession.merge(order)
                # validator already ensured that cae_percentage are the same
                # among linked orders.
                obj.cae_percentage = order.cae_percentage

                obj.import_lines_from_order(order)

            self.dbsession.merge(obj)

            self.dbsession.flush()

            msg = "La facture a été créée, les lignes ont été copiées depuis "
            if len(supplier_orders_ids) < 2:
                msg += "la commande fournisseur."
            else:
                msg += "les commandes fournisseurs."
            self.request.session.flash(msg)

            redirect_url = get_supplier_doc_url(
                self.request,
                doc=obj,
            )
        else:
            redirect_url = self.request.route_path(
                COMPANY_COLLECTION_ROUTE, id=company.id, _query={"action": "new_step2"}
            )
        return HTTPFound(redirect_url)


class SupplierInvoiceAddStep2View(BaseSupplierInvoiceAddMixin, BaseAddView):
    """
    Optional view ; with supplier selector

    Displayed only when no supplier order has been selected at previous step.
    """

    msg = "La facture fournisseur a été créée"

    schema = get_supplier_invoice_add_by_supplier_schema()

    def create_instance(self):
        return SupplierInvoice(
            company_id=self.context.id,
            payer=get_default_employee_from_request(self.request),
        )

    def redirect(self, appstruct, obj):
        url = get_supplier_doc_url(
            self.request,
            doc=obj,
        )
        return HTTPFound(url)


class SupplierInvoiceEditView(BaseView, JsAppViewMixin, TreeMixin):
    """
    Can act as edit view or readonly view (eg: waiting for validation).
    """

    def context_url(self, _query: Dict[str, str] = {}):
        return get_supplier_doc_url(self.request, api=True, _query=_query)

    @property
    def title(self):
        current_inv = self.current()
        label = current_inv.remote_invoice_number
        if current_inv.internal:
            label += " (Facture interne)"
        if not label:
            label = "Facture fournisseur"
        return label

    @property
    def tree_url(self):
        current_inv = self.current()
        return get_supplier_doc_url(self.request, doc=current_inv)

    def current(self):
        """Return the supplier invoice to use in the breadcrumb (TreeMixin) implementations"""
        if isinstance(self.context, SupplierInvoice):
            result = self.context
        elif hasattr(self.context, "parent"):
            result = self.context.parent
        else:
            raise Exception(f"Can't find current supplier invoice in {self.context}")
        return result

    def more_js_app_options(self):
        return dict(
            edit=bool(self.request.has_permission("edit.supplier_invoice")),
        )

    def internal_source_document_link(self):
        if self.context.internal:
            source_doc = self.context.source
            typ_ = get_task_view_type(source_doc)
            if self.request.has_permission(f"view.{typ_}", source_doc):
                url = get_task_url(self.request, source_doc, suffix="/general")

                return Link(
                    url=url,
                    label=f"Facture associée {source_doc.official_number}",
                    title="Voir la facture associée",
                    icon=None,
                )
        else:
            return None

    def __call__(self):
        populate_actionmenu(self.request)
        supplier_invoice_resources.need()
        return dict(
            title=self.title,
            context=self.context,
            js_app_options=self.get_js_app_options(),
            internal_source_document_link=self.internal_source_document_link(),
        )


class SupplierInvoiceDuplicateView(DuplicateView):
    route_name = "/supplier_invoices/{id}"
    message = "vous avez été redirigé vers la nouvelle facture fournisseur"


class SupplierInvoiceListTools(SupplierDocListTools):
    model_class = SupplierInvoice

    sort_columns = {
        "official_number": "official_number",
        "remote_invoice_number": "remote_invoice_number",
        "total_ht": "total_ht",
        "total_tva": "total_tva",
        "total": "total",
    }
    sort_columns.update(SupplierDocListTools.sort_columns)

    # sort by invoice date rather than creation date
    default_sort = "date"
    default_direction = "desc"

    def sort_by_total_tva(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.tva,
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.tva))
        return query

    def sort_by_total_ht(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.ht,
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.ht))
        return query

    def sort_by_total(self, query, appstruct):
        sort_direction = self._get_sort_direction(appstruct)
        self.logger.debug("  + Direction : %s" % sort_direction)
        query = query.outerjoin(SupplierInvoice.lines).options(
            contains_eager(SupplierInvoice.lines).load_only(
                SupplierInvoiceLine.ht, SupplierInvoiceLine.tva
            )
        )

        if sort_direction == "asc":
            func = asc
        else:
            func = desc

        query = query.order_by(func(SupplierInvoiceLine.ht + SupplierInvoiceLine.tva))
        return query

    def filter_official_number(self, query, appstruct):
        official_number = appstruct.get("official_number")
        if official_number:
            query = query.filter_by(official_number=official_number)
        return query

    def filter_remote_invoice_number(self, query, appstruct):
        remote_invoice_number = appstruct.get("remote_invoice_number")
        if remote_invoice_number:
            query = query.filter_by(remote_invoice_number=remote_invoice_number)
        return query

    def filter_combined_paid_status(self, query, appstruct):
        status = appstruct.get("combined_paid_status")
        if status == "paid":
            query = query.filter_by(paid_status="resulted")
        elif status == "supplier_topay":
            query = query.filter(
                SupplierInvoice.supplier_paid_status != "resulted",
                SupplierInvoice.cae_percentage > 0,
            )
        elif status == "worker_topay":
            query = query.filter(
                SupplierInvoice.worker_paid_status != "resulted",
                SupplierInvoice.cae_percentage < 100,
            )
        return query


def stream_supplier_invoice_actions(request, supplier_invoice):
    yield Link(
        get_supplier_doc_url(request, doc=supplier_invoice),
        "Voir ou modifier",
        icon="arrow-right",
    )
    delete_allowed = request.has_permission(
        "delete.supplier_invoice",
        supplier_invoice,
    )
    if delete_allowed:
        yield POSTButton(
            get_supplier_doc_url(
                request, doc=supplier_invoice, _query={"action": "delete"}
            ),
            "Supprimer",
            title="Supprimer définitivement cette facture ?",
            icon="trash-alt",
            css="negative",
            confirm="Êtes-vous sûr de vouloir supprimer cette facture ?",
        )


class BaseSupplierInvoiceListView(
    SupplierInvoiceListTools,
    BaseListView,
):
    title = "Liste des factures fournisseurs"
    add_template_vars = [
        "title",
        "stream_actions",
        "stream_main_actions",
        "stream_more_actions",
    ]

    def stream_actions(self, supplier_invoice):
        return stream_supplier_invoice_actions(self.request, supplier_invoice)

    def get_export_path(self, extension):
        return self.request.route_path(
            COLLECTION_EXPORT_ROUTE,
            extension=extension,
            _query=self.request.GET,
        )

    def stream_main_actions(self):
        return []

    def stream_more_actions(self):
        yield Link(
            self.get_export_path(extension="csv"),
            icon="file-csv",
            label="Liste des factures fournisseurs (CSV)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export CSV des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="xlsx"),
            icon="file-excel",
            label="Liste des factures fournisseurs (Excel)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export Excel des factures de la liste",
        )
        yield Link(
            self.get_export_path(extension="ods"),
            icon="file-spreadsheet",
            label="Liste des factures fournisseurs (ODS)",
            css="btn icon_only mobile",
            popup=True,
            title="Générer un export ODS des factures de la liste",
        )


class AdminSupplierInvoiceListView(BaseSupplierInvoiceListView):
    """
    Global list of SupplierOrder from all companies
    """

    is_admin_view = True
    add_template_vars = BaseSupplierInvoiceListView.add_template_vars + [
        "is_admin_view",
    ]

    schema = get_supplier_invoice_list_schema(is_global=True)

    def query(self):
        return SupplierInvoice.query()

    def stream_main_actions(self):
        yield Link(
            DISPATCH_ROUTE,
            icon="dispatch",
            label="Ventiler une facture fournisseur",
            css="btn btn-primary",
        )


class CompanySupplierInvoiceListView(BaseSupplierInvoiceListView):
    """
    Company-scoped list of SupplierOrder
    """

    schema = get_supplier_invoice_list_schema(is_global=False)

    def query(self):
        company = self.request.context
        query = SupplierInvoice.query()
        return query.filter_by(company_id=company.id)

    def stream_main_actions(self):
        yield Link(
            self.request.route_path(
                COMPANY_COLLECTION_ROUTE,
                _query=dict(action="new"),
                id=self.request.context.id,
            ),
            icon="plus",
            label="Ajouter une facture fournisseur",
            css="btn btn-primary",
        )

    def get_export_path(self, extension):
        return self.request.route_path(
            COMPANY_COLLECTION_EXPORT_ROUTE,
            id=self.request.context.id,
            extension=extension,
            _query=self.request.GET,
        )


class GlobalSupplierInvoicesCsvView(
    AsyncJobMixin,
    SupplierInvoiceListTools,
    BaseListView,
):
    model = SupplierInvoice
    file_format = "csv"
    filename = "factures_frns_"
    schema = get_supplier_invoice_list_schema(is_global=True)

    def query(self):
        query = self.request.dbsession.query(SupplierInvoice)
        query = query.options(load_only(SupplierInvoice.id))
        return query

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        all_ids = [elem.id for elem in query]
        logger.debug("    + All_ids where collected : {0}".format(all_ids))
        if not all_ids:
            return self.show_error("Aucune facture ne correspond à cette requête")

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp
        else:
            logger.debug("    + In the GlobalInvoicesCsvView._build_return_value")
            job_result = self.initialize_job_result(FileGenerationJob)

            logger.debug("    + Delaying the export_to_file task")
            celery_job = export_to_file.delay(
                job_result.id,
                "supplier_invoices",
                all_ids,
                self.filename,
                self.file_format,
            )
            return self.redirect_to_job_watch(celery_job, job_result)


class GlobalSupplierInvoicesExcelView(GlobalSupplierInvoicesCsvView):
    file_format = "xlsx"


class GlobalSupplierInvoiceOdsView(GlobalSupplierInvoicesCsvView):
    file_format = "ods"


class CompanySupplierInvoiceCsvView(GlobalSupplierInvoicesCsvView):
    file_format = "csv"
    schema = get_supplier_invoice_list_schema(is_global=False)

    def query(self):
        company = self.request.context
        query = SupplierInvoice.query()
        return query.filter_by(company_id=company.id)


class CompanySupplierInvoiceExcelView(CompanySupplierInvoiceCsvView):
    file_format = "xlsx"


class CompanySupplierInvoiceOdsView(CompanySupplierInvoiceCsvView):
    file_format = "ods"


class SupplierInvoiceDeleteView(DeleteView):
    delete_msg = "La facture fournisseur a bien été supprimée"

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                COMPANY_COLLECTION_ROUTE, id=self.context.company.id
            )
        )


SUPPLIER_INVOICE_DISPATCH_GRID = (
    (
        ("date", 2),
        ("supplier_id", 10),
    ),
    (("remote_invoice_number", 6), ("invoice_file", 6)),
    (
        ("total_ht", 6),
        ("total_tva", 6),
    ),
    (("lines", 12),),
)


class SupplierInvoiceDispatchView(BaseFormView):
    """
    Used when an EA receives a global supplier invoice that needs to be split,
    enDi-wise, into several supplier invoices.
    """

    add_template_vars = ("title",)
    title = "Ventiler une facture fournisseur"
    schema = SupplierInvoiceDispatchSchema(
        widget=deform_extensions.GridFormWidget(
            named_grid=SUPPLIER_INVOICE_DISPATCH_GRID
        ),
        title="Réception d'une commande fournisseur",
    )

    def before(self, form):
        dispatch_supplier_invoice_js.need()

    @staticmethod
    def _group_lines_by_company(lines):
        ret = {}
        for line in lines:
            try:
                ret[line["company_id"]].append(line)
            except KeyError:
                ret[line["company_id"]] = [line]
        return ret

    def submit_success(self, appstruct):
        reference_supplier = Supplier.query().get(appstruct["supplier_id"])
        created_invoices = []

        indexed_lines = self._group_lines_by_company(appstruct["lines"])
        for company_id, lines in list(indexed_lines.items()):
            supplier = (
                Supplier.query()
                .filter_by(
                    registration=reference_supplier.registration,
                    company_id=company_id,
                )
                .first()
            )
            if supplier is None:
                # Copy minimal information to avoid data leak
                supplier = Supplier(
                    company_id=company_id,
                    company_name=reference_supplier.company_name,
                    registration=reference_supplier.registration,
                )
                self.dbsession.add(supplier)

            invoice = SupplierInvoice(
                date=appstruct["date"],
                company=Company.get(company_id),
                supplier=supplier,
                remote_invoice_number=appstruct.get("remote_invoice_number", ""),
            )
            controller = FileController(self.request)
            controller.save({"upload": appstruct["invoice_file"]}, parent=invoice)
            self.dbsession.add(invoice)

            for line in lines:
                SupplierInvoiceLine(
                    supplier_invoice=invoice,
                    description=line["description"],
                    ht=line["ht"],
                    tva=line["tva"],
                    type_id=line["type_id"],
                )
                # invoice.lines.append(new_line)
            created_invoices.append(invoice)

        invoices_descriptions = [
            f"{invoice.company.name}/{invoice.remote_invoice_number}"
            for invoice in created_invoices
        ]

        self.session.flash(
            "Les factures suivantes ont été créées : {}".format(
                " ".join(invoices_descriptions)
            )
        )
        return HTTPFound("/supplier_invoices")


class SupplierInvoiceSetTypesView(BaseFormView):
    """
    Base view for setting product codes (on supplier_invoices)

    context

        invoice or cancelinvoice
    """

    schema = SetTypesSchema()

    @property
    def title(self):
        return (
            "Configuration des types de dépenses de la facture fournisseur "
            "{}".format(self.context.official_number)
        )

    def before(self, form):
        form.set_appstruct({"lines": [line.appstruct() for line in self.context.lines]})
        self.request.actionmenu.add(
            ViewLink(
                "Revenir au document",
                path="/supplier_invoices/{id}",
                id=self.context.id,
            )
        )

    def submit_success(self, appstruct):
        for line in appstruct["lines"]:
            line_id = line.get("id")
            type_id = line.get("type_id")
            if line_id is not None and type_id is not None:
                line = SupplierInvoiceLine.get(line_id)
                if line.supplier_invoice == self.context:
                    line.type_id = type_id
                    self.request.dbsession.merge(line)
                else:
                    logger.error(
                        "Possible break in attempt: trying to set product id "
                        "on the wrong supplier_invoice line (not belonging to "
                        "this supplier_invoice)"
                    )
        return HTTPFound(get_supplier_doc_url(self.request))


def includeme(config):
    # Admin views
    config.add_view(
        AdminSupplierInvoiceListView,
        request_method="GET",
        route_name=COLLECTION_ROUTE,
        permission="admin.supplier_invoice",
        renderer="/supply/supplier_invoices.mako",
    )
    config.add_view(
        GlobalSupplierInvoicesCsvView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=csv",
        permission="admin.supplier_invoice",
    )
    config.add_view(
        GlobalSupplierInvoicesExcelView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=xlsx",
        permission="admin.supplier_invoice",
    )
    config.add_view(
        GlobalSupplierInvoiceOdsView,
        route_name=COLLECTION_EXPORT_ROUTE,
        match_param="extension=ods",
        permission="admin.supplier_invoice",
    )

    config.add_view(
        SupplierInvoiceAddView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_param="action=new",
        permission="add.supplier_invoice",
        renderer="base/formpage.mako",
    )
    config.add_view(
        SupplierInvoiceAddStep2View,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_param="action=new_step2",
        permission="add.supplier_invoice",
        renderer="base/formpage.mako",
    )
    config.add_view(
        CompanySupplierInvoiceListView,
        route_name=COMPANY_COLLECTION_ROUTE,
        request_method="GET",
        renderer="/supply/supplier_invoices.mako",
        permission="list.supplier_invoice",
    )
    config.add_view(
        CompanySupplierInvoiceCsvView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=csv",
        permission="list.supplier_invoice",
    )
    config.add_view(
        CompanySupplierInvoiceExcelView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=xlsx",
        permission="list.supplier_invoice",
    )
    config.add_view(
        CompanySupplierInvoiceOdsView,
        route_name=COMPANY_COLLECTION_EXPORT_ROUTE,
        match_param="extension=ods",
        permission="list.supplier_invoice",
    )

    config.add_view(
        SupplierInvoiceEditView,
        route_name=ITEM_ROUTE,
        renderer="/supply/supplier_invoice.mako",
        permission="view.supplier_invoice",
        layout="opa",
    )
    config.add_view(
        SupplierInvoiceSetTypesView,
        route_name=f"{ITEM_ROUTE}/set_types",
        renderer="base/formpage.mako",
        permission="set_types.supplier_invoice",
    )

    config.add_view(
        SupplierInvoiceDeleteView,
        route_name=ITEM_ROUTE,
        request_param="action=delete",
        permission="delete.supplier_invoice",
        request_method="POST",
        require_csrf=True,
    )
    config.add_view(
        SupplierInvoiceDuplicateView,
        route_name=ITEM_ROUTE,
        request_param="action=duplicate",
        permission="duplicate.supplier_invoice",
        request_method="POST",
        require_csrf=True,
    )

    # File attachment
    config.add_view(
        FileUploadView,
        route_name=f"{ITEM_ROUTE}/addfile",
        renderer="base/formpage.mako",
        permission="add.file",
    )

    config.add_view(
        SupplierInvoiceDispatchView,
        route_name=DISPATCH_ROUTE,
        permission="admin.supplier_invoice",
        renderer="supply/dispatch_supplier_invoice.mako",
    )
    config.add_admin_menu(
        parent="sale",
        order=3,
        label="Factures fournisseurs",
        href=COLLECTION_ROUTE,
        routes_prefixes=[ITEM_ROUTE],
    )
    config.add_company_menu(
        parent="supply",
        order=2,
        label="Factures fournisseurs",
        route_name=COMPANY_COLLECTION_ROUTE,
        route_id_key="company_id",
        routes_prefixes=[ITEM_ROUTE],
    )
