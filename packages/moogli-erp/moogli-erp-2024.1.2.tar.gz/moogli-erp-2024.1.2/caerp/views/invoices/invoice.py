"""
    Invoice views
"""
import logging

from pyramid.httpexceptions import HTTPFound

from ...utils.datetimes import format_date
from caerp.models.task import (
    Invoice,
    Estimation,
)
from caerp.models.project.business import Business
from caerp.utils.widgets import (
    ViewLink,
    Link,
)
from caerp.forms.tasks.invoice import (
    EstimationAttachSchema,
    get_add_edit_invoice_schema,
)
from caerp.resources import task_preview_css
from caerp.views import (
    BaseView,
    BaseEditView,
    BaseFormView,
    submit_btn,
    cancel_btn,
    add_panel_page_view,
)
from caerp.views.business.routes import BUSINESS_ITEM_ROUTE
from caerp.views.business.business import BusinessOverviewView
from caerp.views.task.utils import get_task_url

from caerp.views.task.views import (
    TaskAddView,
    TaskEditView,
    TaskDeleteView,
    TaskFilesView,
    TaskGeneralView,
    TaskPdfView,
    TaskPdfDevView,
    TaskDuplicateView,
    TaskPreviewView,
    TaskSetMetadatasView,
    TaskSetProductsView,
    TaskSetDraftView,
    TaskMoveToPhaseView,
    TaskZipFileView,
    BaseTaskHtmlTreeMixin,
    TaskFileUploadView,
)
from caerp.views.company.routes import (
    COMPANY_INVOICE_ADD_ROUTE,
)
from .routes import (
    CINV_ITEM_ROUTE,
    INVOICE_ITEM_ROUTE,
    API_INVOICE_ADD_ROUTE,
    INVOICE_ITEM_GENERAL_ROUTE,
    INVOICE_ITEM_PREVIEW_ROUTE,
    INVOICE_ITEM_ACCOUNTING_ROUTE,
    INVOICE_ITEM_PAYMENT_ROUTE,
    INVOICE_ITEM_FILES_ROUTE,
)


logger = log = logging.getLogger(__name__)


class InvoiceAddView(TaskAddView):
    """
    Invoice add view
    context is a project or company
    """

    factory = Invoice
    title = "Nouvelle facture"

    def _after_flush(self, invoice):
        """
        Launch after the new invoice has been flushed
        """
        logger.debug("  + Invoice successfully added : {0}".format(invoice.id))

    def get_api_url(self, _query: dict = {}) -> str:
        return self.request.route_path(
            API_INVOICE_ADD_ROUTE, id=self._get_company_id(), _query=_query
        )

    def get_parent_link(self):
        result = super().get_parent_link()
        if result is not None:
            return result

        referrer = self.request.referrer
        current_url = self.request.current_route_url(_query={})
        if referrer and referrer != current_url and "login" not in referrer:
            if "invoices" in referrer:
                label = "Revenir à la liste des factures"
            elif "dashboard" in referrer:
                label = "Revenir à l'accueil"
            else:
                label = "Revenir en arrière"
            result = Link(referrer, label)
        else:
            result = Link(
                self.request.route_path(COMPANY_INVOICE_ADD_ROUTE, id=self.context.id),
                "Revenir à la liste des factures",
            )
        return result


class InvoiceEditView(TaskEditView):
    route_name = INVOICE_ITEM_ROUTE

    @property
    def title(self):
        customer = self.context.customer
        customer_label = customer.label
        if customer.code is not None:
            customer_label += " ({0})".format(customer.code)
        return (
            "Modification de la {tasktype_label} « {task.name} » avec le "
            "client {customer}".format(
                task=self.context,
                customer=customer_label,
                tasktype_label=self.context.get_type_label().lower(),
            )
        )

    def discount_api_url(self):
        return get_task_url(self.request, suffix="/discount_lines", api=True)

    def post_ttc_api_url(self):
        return get_task_url(self.request, suffix="/post_ttc_lines", api=True)

    def get_related_estimation_url(self):
        return self.context_url({"related_estimation": "1"})

    def get_js_app_options(self) -> dict:
        options = super().get_js_app_options()
        options.update(
            {
                "invoicing_mode": self.context.invoicing_mode,
                "related_estimation_url": self.get_related_estimation_url(),
            }
        )
        if not self.context.has_progress_invoicing_plan():
            options["discount_api_url"] = self.discount_api_url()
            options["post_ttc_api_url"] = self.post_ttc_api_url()
        return options


class InvoiceDeleteView(TaskDeleteView):
    msg = "La facture {context.name} a bien été supprimée."

    def on_delete(self):
        self.business = self.context.business
        return super().on_delete()

    def redirect(self):
        if self.business.is_visible():
            # l'affaire peut avoir été supprimée mais self.business pointe sur
            # un objet qui ne correspond plus à rien en base
            refreshed_business = Business.get(self.business.id)
            if refreshed_business:
                return HTTPFound(
                    self.request.route_path(BUSINESS_ITEM_ROUTE, id=self.business.id)
                )
        return super().redirect()

    def pre_delete(self):
        """
        If an estimation is attached to this invoice, ensure geninv is set to
        False
        """
        self.business = self.context.business
        if getattr(self.context, "estimation", None) is not None:
            if len(self.context.estimation.invoices) == 1:
                self.context.estimation.geninv = False
                self.request.dbsession.merge(self.context.estimation)


# VUE pour les factures validées
def get_title(invoice):
    return "Facture numéro {0}".format(invoice.official_number)


class InvoiceGeneralView(TaskGeneralView):
    route_name = INVOICE_ITEM_GENERAL_ROUTE
    file_route_name = INVOICE_ITEM_FILES_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class InvoicePreviewView(TaskPreviewView):
    route_name = INVOICE_ITEM_PREVIEW_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class InvoiceAccountingView(BaseView, BaseTaskHtmlTreeMixin):
    route_name = INVOICE_ITEM_ACCOUNTING_ROUTE

    @property
    def title(self):
        return get_title(self.current())

    def __call__(self):
        self.populate_navigation()
        return {"title": self.title}


class InvoicePaymentView(BaseView, BaseTaskHtmlTreeMixin):
    route_name = INVOICE_ITEM_PAYMENT_ROUTE

    @property
    def title(self):
        return get_title(self.current())

    def __call__(self):
        self.populate_navigation()
        return {"title": self.title}


class InvoiceFilesView(TaskFilesView):
    route_name = INVOICE_ITEM_FILES_ROUTE

    @property
    def title(self):
        return get_title(self.current())


class InvoiceDuplicateView(TaskDuplicateView):
    @property
    def label(self):
        return f"la {self.context.get_type_label().lower()}"


class InvoicePdfView(TaskPdfView):
    pass


def gencinv_view(context, request):
    """
    Cancelinvoice generation view
    """
    try:
        cancelinvoice = context.gen_cancelinvoice(request, request.identity)
    except:  # noqa
        logger.exception(
            "Error while generating a cancelinvoice for {0}".format(context.id)
        )
        request.session.flash(
            "Erreur à la génération de votre avoir, contactez votre administrateur",
            "error",
        )
        return HTTPFound(request.route_path(INVOICE_ITEM_ROUTE, id=context.id))
    return HTTPFound(request.route_path(CINV_ITEM_ROUTE, id=cancelinvoice.id))


class InvoiceSetTreasuryiew(BaseEditView):
    """
    View used to set treasury related informations

    context

        An invoice

    perms

        set_treasury.invoice
    """

    factory = Invoice
    schema = get_add_edit_invoice_schema(
        includes=("financial_year",),
        title="Modifier l'année fiscale de la facture",
    )

    def redirect(self, appstruct):
        return HTTPFound(get_task_url(self.request, suffix="/general"))

    def before(self, form):
        BaseEditView.before(self, form)
        self.request.actionmenu.add(
            ViewLink(
                label=f"Revenir à la {self.context.get_type_label().lower()}",
                url=get_task_url(self.request, suffix="/accounting"),
            )
        )

    @property
    def title(self):
        return "{} numéro {} en date du {}".format(
            self.context.get_type_label(),
            self.context.official_number,
            format_date(self.context.date),
        )


class InvoiceSetMetadatasView(TaskSetMetadatasView):
    """
    View used for editing invoice metadatas
    """

    @property
    def title(self):
        return "Modification de la {tasktype_label} {task.name}".format(
            task=self.context,
            tasktype_label=self.context.get_type_label().lower(),
        )


class InvoiceSetProductsView(TaskSetProductsView):
    @property
    def title(self):
        return "Configuration des codes produits pour la facture {0.name}".format(
            self.context
        )


class InvoiceAttachEstimationView(BaseFormView):
    schema = EstimationAttachSchema
    buttons = (
        submit_btn,
        cancel_btn,
    )

    def before(self, form):
        self.request.actionmenu.add(
            ViewLink(
                label="Revenir à la facture",
                url=get_task_url(
                    self.request,
                    suffix="/general",
                ),
            )
        )
        if self.context.estimation_id:
            form.set_appstruct({"estimation_id": self.context.estimation_id})

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                "/invoices/{id}/general",
                id=self.context.id,
            )
        )

    def submit_success(self, appstruct):
        estimation_id = appstruct.get("estimation_id")
        self.context.estimation_id = estimation_id
        if estimation_id is not None:
            estimation = Estimation.get(estimation_id)
            estimation.geninv = True
            self.request.dbsession.merge(estimation)
        self.request.dbsession.merge(self.context)
        return self.redirect()

    def cancel_success(self, appstruct):
        return self.redirect()

    cancel_failure = cancel_success


class InvoiceAdminView(BaseEditView):
    """
    Vue pour l'administration de factures /invoices/id/admin

    Vue accessible aux utilisateurs admin
    """

    factory = Invoice
    schema = get_add_edit_invoice_schema(
        title="Formulaire d'édition forcée de devis/factures/avoirs",
        help_msg="Les montants sont *10^5   10 000==1€",
    )


def add_routes(config):
    """
    add module related routes
    """
    for extension in ("pdf", "preview"):
        route = f"{INVOICE_ITEM_ROUTE}.{extension}"
        config.add_route(route, route, traverse="/tasks/{id}")
    for action in (
        "addfile",
        "delete",
        "duplicate",
        "admin",
        "set_treasury",
        "set_products",
        "gencinv",
        "set_metadatas",
        "attach_estimation",
        "set_draft",
        "move",
        "sync_price_study",
        "archive.zip",
    ):
        route = f"{INVOICE_ITEM_ROUTE}/{action}"
        config.add_route(route, route, traverse="/tasks/{id}")


def includeme(config):
    add_routes(config)

    config.add_view(
        InvoiceAddView,
        route_name=COMPANY_INVOICE_ADD_ROUTE,
        renderer="tasks/add.mako",
        permission="add.invoice",
        layout="vue_opa",
    )

    config.add_tree_view(
        InvoiceEditView,
        parent=BusinessOverviewView,
        renderer="tasks/form.mako",
        permission="view.invoice",
        context=Invoice,
        layout="opa",
    )

    config.add_view(
        InvoiceDeleteView,
        route_name="/invoices/{id}/delete",
        permission="delete.invoice",
        require_csrf=True,
        request_method="POST",
        context=Invoice,
    )

    config.add_view(
        InvoiceAdminView,
        route_name="/invoices/{id}/admin",
        renderer="base/formpage.mako",
        permission="admin",
        context=Invoice,
    )

    config.add_view(
        InvoiceDuplicateView,
        route_name="/invoices/{id}/duplicate",
        permission="duplicate.invoice",
        renderer="tasks/duplicate.mako",
        context=Invoice,
        layout="default",
    )

    add_panel_page_view(
        config,
        "task_pdf_content",
        js_resources=(task_preview_css,),
        route_name="/invoices/{id}.preview",
        permission="view.invoice",
        context=Invoice,
    )

    config.add_view(
        InvoicePdfView,
        route_name="/invoices/{id}.pdf",
        permission="view.invoice",
        context=Invoice,
    )

    config.add_view(
        TaskPdfDevView,
        route_name="/invoices/{id}.preview",
        request_param="action=dev_pdf",
        renderer="panels/task/pdf/content_wrapper.mako",
        permission="view.invoice",
        context=Invoice,
    )

    config.add_view(
        TaskFileUploadView,
        route_name="/invoices/{id}/addfile",
        renderer="base/formpage.mako",
        permission="add.file",
        context=Invoice,
    )

    config.add_view(
        gencinv_view,
        route_name="/invoices/{id}/gencinv",
        permission="gencinv.invoice",
        require_csrf=True,
        request_method="POST",
        context=Invoice,
    )

    config.add_view(
        InvoiceSetTreasuryiew,
        route_name="/invoices/{id}/set_treasury",
        permission="set_treasury.invoice",
        renderer="base/formpage.mako",
        context=Invoice,
    )
    config.add_view(
        InvoiceSetMetadatasView,
        route_name="/invoices/{id}/set_metadatas",
        permission="view.invoice",
        renderer="tasks/duplicate.mako",
        context=Invoice,
    )
    config.add_view(
        TaskSetDraftView,
        route_name="/invoices/{id}/set_draft",
        permission="draft.invoice",
        require_csrf=True,
        request_method="POST",
        context=Invoice,
    )

    config.add_view(
        InvoiceSetProductsView,
        route_name="/invoices/{id}/set_products",
        permission="set_treasury.invoice",
        renderer="base/formpage.mako",
        context=Invoice,
    )
    config.add_view(
        InvoiceAttachEstimationView,
        route_name="/invoices/{id}/attach_estimation",
        permission="view.invoice",
        renderer="base/formpage.mako",
        context=Invoice,
    )
    config.add_view(
        TaskMoveToPhaseView,
        route_name="/invoices/{id}/move",
        permission="view.invoice",
        require_csrf=True,
        request_method="POST",
        context=Invoice,
    )
    config.add_view(
        TaskZipFileView,
        route_name="/invoices/{id}/archive.zip",
        permission="view.invoice",
        context=Invoice,
    )

    config.add_tree_view(
        InvoiceGeneralView,
        parent=BusinessOverviewView,
        layout="invoice",
        renderer="tasks/invoice/general.mako",
        permission="view.node",
        context=Invoice,
    )
    config.add_tree_view(
        InvoicePreviewView,
        parent=BusinessOverviewView,
        layout="invoice",
        renderer="tasks/preview.mako",
        permission="view.node",
        context=Invoice,
    )
    config.add_tree_view(
        InvoiceAccountingView,
        parent=BusinessOverviewView,
        layout="invoice",
        renderer="tasks/invoice/accounting.mako",
        permission="view.node",
        context=Invoice,
    )
    config.add_tree_view(
        InvoicePaymentView,
        parent=BusinessOverviewView,
        layout="invoice",
        renderer="tasks/invoice/payment.mako",
        permission="view.node",
        context=Invoice,
    )
    config.add_tree_view(
        InvoiceFilesView,
        parent=BusinessOverviewView,
        layout="invoice",
        renderer="tasks/files.mako",
        permission="view.node",
        context=Invoice,
    )
