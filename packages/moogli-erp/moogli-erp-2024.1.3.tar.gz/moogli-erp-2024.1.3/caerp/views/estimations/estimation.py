"""
Estimation views


Estimation datas edition :
    date
    address
    customer
    object
    note
    mentions
    ....

Estimation line edition :
    description
    quantity
    cost
    unity
    tva
    ...

Estimation line group edition :
    title
    description

Estimation discount edition

Estimation payment edition

"""
import logging

from pyramid.httpexceptions import HTTPFound
from caerp.forms.tasks.estimation import InvoiceAttachSchema
from caerp.models.task import (
    Estimation,
    PaymentLine,
    Invoice,
)
from caerp.utils.widgets import (
    ViewLink,
    Link,
)
from caerp.resources import (
    estimation_signed_status_js,
    task_preview_css,
)
from caerp.forms.tasks.estimation import get_edit_estimation_schema
from caerp.controllers.state_managers import (
    get_signed_allowed_actions,
)
from caerp.views import (
    BaseEditView,
    BaseFormView,
    submit_btn,
    cancel_btn,
    add_panel_page_view,
)
from caerp.views.company.routes import (
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_ESTIMATIONS_ROUTE,
)
from caerp.views.estimations.routes import (
    API_ADD_ROUTE,
    ESTIMATION_ITEM_ROUTE,
    ESTIMATION_ITEM_GENERAL_ROUTE,
    ESTIMATION_ITEM_PREVIEW_ROUTE,
    ESTIMATION_ITEM_FILES_ROUTE,
)

from caerp.views.business.business import BusinessOverviewView
from caerp.views.task.utils import (
    get_task_url,
)
from caerp.views.task.views import (
    TaskAddView,
    TaskEditView,
    TaskDeleteView,
    TaskGeneralView,
    TaskPreviewView,
    TaskFilesView,
    TaskPdfView,
    TaskDuplicateView,
    TaskSetMetadatasView,
    TaskSetDraftView,
    TaskMoveToPhaseView,
    TaskFileUploadView,
)

log = logger = logging.getLogger(__name__)


class EstimationAddView(TaskAddView):
    """
    Estimation add view
    context is a project or company
    """

    factory = Estimation
    title = "Nouveau devis"

    def _after_flush(self, estimation):
        """
        Launch after the new estimation has been flushed
        """
        logger.debug("  + Estimation successfully added : {0}".format(estimation.id))

    def get_api_url(self, _query: dict = {}) -> str:
        return self.request.route_path(
            API_ADD_ROUTE, id=self._get_company_id(), _query=_query
        )

    def get_parent_link(self):
        result = super().get_parent_link()
        if result is not None:
            return result

        referrer = self.request.referrer
        current_url = self.request.current_route_url(_query={})
        if referrer and referrer != current_url and "login" not in referrer:
            if "estimations" in referrer:
                label = "Revenir à la liste des devis"
            elif "dashboard" in referrer:
                label = "Revenir à l'accueil"
            else:
                label = "Revenir en arrière"
            result = Link(referrer, label)
        else:
            result = Link(
                self.request.route_path(COMPANY_ESTIMATIONS_ROUTE, id=self.context.id),
                "Revenir à la liste des devis",
            )
        return result


class EstimationEditView(TaskEditView):
    route_name = ESTIMATION_ITEM_ROUTE

    @property
    def title(self):
        customer = self.context.customer
        customer_label = customer.label
        if customer.code is not None:
            customer_label += " ({0})".format(customer.code)
        return (
            "Modification du {tasktype_label} « {task.name} » avec le client "
            "{customer}".format(
                task=self.context,
                customer=customer_label,
                tasktype_label=self.context.get_type_label().lower(),
            )
        )

    def _before(self):
        """
        Ensure some stuff on the current context
        """
        if not self.context.payment_lines:
            self.context.payment_lines = [
                PaymentLine(description="Solde", amount=self.context.ttc)
            ]
            self.request.dbsession.merge(self.context)
            self.request.dbsession.flush()

    def discount_api_url(self):
        return get_task_url(self.request, suffix="/discount_lines", api=True)

    def payment_lines_api_url(self):
        return get_task_url(self.request, suffix="/payment_lines", api=True)

    def get_js_app_options(self) -> dict:
        options = super().get_js_app_options()
        options.update(
            {
                "discount_api_url": self.discount_api_url(),
                "payment_lines_api_url": self.payment_lines_api_url(),
            }
        )
        return options


class EstimationAdminView(BaseEditView):
    factory = Estimation
    schema = get_edit_estimation_schema(isadmin=True)


class EstimationGeneralView(TaskGeneralView):
    file_route_name = ESTIMATION_ITEM_FILES_ROUTE
    route_name = ESTIMATION_ITEM_GENERAL_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.internal_number}"

    def get_actions(self):
        estimation_signed_status_js.need()
        actions = []
        for action in get_signed_allowed_actions(self.request, self.context):
            actions.append(action)
        return actions

    def __call__(self):
        result = super().__call__()
        # On peut récupérer un HTTPFound de la classe parente
        if isinstance(result, dict):
            result["actions"] = self.get_actions()
        return result


class EstimationPreviewView(TaskPreviewView):
    route_name = ESTIMATION_ITEM_PREVIEW_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.internal_number}"


class EstimationFilesView(TaskFilesView):
    route_name = ESTIMATION_ITEM_FILES_ROUTE

    @property
    def title(self):
        return f"Devis {self.context.internal_number}"


class EstimationPdfView(TaskPdfView):
    pass


class EstimationDuplicateView(TaskDuplicateView):
    label = "le devis"


class EstimationSetMetadatasView(TaskSetMetadatasView):
    @property
    def title(self):
        return "Modification du {tasktype_label} {task.name}".format(
            task=self.context,
            tasktype_label=self.context.get_type_label().lower(),
        )


class EstimationAttachInvoiceView(BaseFormView):
    schema = InvoiceAttachSchema()
    buttons = (
        submit_btn,
        cancel_btn,
    )

    def before(self, form):
        self.request.actionmenu.add(
            ViewLink(
                label="Revenir au devis",
                url=get_task_url(self.request, suffix="/general"),
            )
        )
        form.set_appstruct(
            {"invoice_ids": [str(invoice.id) for invoice in self.context.invoices]}
        )

    def redirect(self):
        return HTTPFound(get_task_url(self.request, suffix="/general"))

    def submit_success(self, appstruct):
        invoice_ids = appstruct.get("invoice_ids")
        for invoice_id in invoice_ids:
            invoice = Invoice.get(invoice_id)
            invoice.estimation_id = self.context.id
            self.request.dbsession.merge(invoice)

        if invoice_ids:
            self.context.geninv = True
            self.request.dbsession.merge(self.context)
        return self.redirect()

    def cancel_success(self, appstruct):
        return self.redirect()

    cancel_failure = cancel_success


def estimation_geninv_view(context, request):
    """
    Invoice generation view : used in shorthanded workflow

    :param obj context: The current context (estimation)
    """
    business = context.gen_business()
    invoices = business.gen_invoices(request, request.identity)

    context.geninv = True
    request.dbsession.merge(context)

    if len(invoices) > 1:
        msg = "{0} factures ont été générées".format(len(invoices))
    else:
        msg = "Une facture a été générée"
    request.session.flash(msg)
    request.dbsession.flush()
    return HTTPFound(request.route_path("/invoices/{id}", id=invoices[0].id))


def estimation_genbusiness_view(context, request):
    """
    Business generation view : used in long handed workflows

    :param obj context: The current estimation
    """
    logger.info("Generating a business for estimation {}".format(context.id))
    business = context.gen_business()
    return HTTPFound(request.route_path("/businesses/{id}", id=business.id))


def add_routes(config):
    """
    Add module's specific routes
    """
    for extension in ("pdf", "preview"):
        route = f"{ESTIMATION_ITEM_ROUTE}.{extension}"
        config.add_route(route, route, traverse="/tasks/{id}")

    for action in (
        "addfile",
        "delete",
        "duplicate",
        "admin",
        "geninv",
        "genbusiness",
        "set_metadatas",
        "attach_invoices",
        "set_draft",
        "move",
        "sync_price_study",
    ):
        route = f"{ESTIMATION_ITEM_ROUTE}/{action}"
        config.add_route(route, route, traverse="/tasks/{id}")


def includeme(config):
    add_routes(config)

    config.add_view(
        EstimationAddView,
        route_name=COMPANY_ESTIMATION_ADD_ROUTE,
        renderer="tasks/add.mako",
        permission="add.estimation",
        layout="vue_opa",
    )
    config.add_tree_view(
        EstimationEditView,
        parent=BusinessOverviewView,
        renderer="tasks/form.mako",
        permission="view.estimation",
        layout="opa",
    )

    config.add_view(
        TaskDeleteView,
        route_name="/estimations/{id}/delete",
        permission="delete.estimation",
        request_method="POST",
        require_csrf=True,
    )

    config.add_view(
        EstimationAdminView,
        route_name="/estimations/{id}/admin",
        renderer="base/formpage.mako",
        permission="admin",
    )

    config.add_view(
        EstimationDuplicateView,
        route_name="/estimations/{id}/duplicate",
        permission="duplicate.estimation",
        renderer="tasks/duplicate.mako",
    )
    add_panel_page_view(
        config,
        "task_pdf_content",
        js_resources=(task_preview_css,),
        route_name="/estimations/{id}.preview",
        permission="view.estimation",
    )

    config.add_view(
        EstimationPdfView,
        route_name="/estimations/{id}.pdf",
        permission="view.estimation",
    )

    config.add_view(
        TaskFileUploadView,
        route_name="/estimations/{id}/addfile",
        renderer="base/formpage.mako",
        permission="add.file",
    )

    config.add_view(
        estimation_geninv_view,
        route_name="/estimations/{id}/geninv",
        permission="geninv.estimation",
        request_method="POST",
        require_csrf=True,
    )

    config.add_view(
        estimation_genbusiness_view,
        route_name="/estimations/{id}/genbusiness",
        permission="genbusiness.estimation",
        require_csrf=True,
        request_method="POST",
    )

    config.add_view(
        EstimationSetMetadatasView,
        route_name="/estimations/{id}/set_metadatas",
        permission="view.estimation",
        renderer="tasks/duplicate.mako",
    )
    config.add_view(
        TaskMoveToPhaseView,
        route_name="/estimations/{id}/move",
        permission="view.estimation",
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        TaskSetDraftView,
        route_name="/estimations/{id}/set_draft",
        permission="draft.estimation",
        require_csrf=True,
        request_method="POST",
    )

    config.add_view(
        EstimationAttachInvoiceView,
        route_name="/estimations/{id}/attach_invoices",
        permission="view.estimation",
        renderer="/base/formpage.mako",
    )

    config.add_tree_view(
        EstimationGeneralView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/estimation/general.mako",
        permission="view.node",
        context=Estimation,
    )
    config.add_tree_view(
        EstimationPreviewView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/preview.mako",
        permission="view.node",
        context=Estimation,
    )
    config.add_tree_view(
        EstimationFilesView,
        parent=BusinessOverviewView,
        layout="estimation",
        renderer="tasks/files.mako",
        permission="view.node",
        context=Estimation,
    )
