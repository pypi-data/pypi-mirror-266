import logging
from pyramid.httpexceptions import HTTPFound
from caerp.forms.project.business import get_business_edit_schema

from caerp.utils.navigation import NavigationHandler
from caerp.models.project.business import Business
from caerp.forms.progress_invoicing import get_new_invoice_schema
from caerp.utils.widgets import (
    ButtonLink,
    POSTButton,
    Link,
)
from caerp.views import (
    TreeMixin,
    BaseView,
    BaseEditView,
    BaseFormView,
)
from caerp.views.task.utils import get_task_url
from caerp.views.project.routes import (
    PROJECT_ITEM_ROUTE,
)
from caerp.views.business.routes import (
    BUSINESS_ITEM_FILE_ROUTE,
    BUSINESS_ITEM_ROUTE,
    BUSINESS_ITEM_OVERVIEW_ROUTE,
    BUSINESS_ITEM_INVOICING_ROUTE,
    BUSINESS_ITEM_INVOICING_ALL_ROUTE,
    BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
    BUSINESS_ITEM_ESTIMATION_ROUTE,
)
from caerp.views.project.project import ProjectEntryPointView


logger = logging.getLogger(__name__)


class BusinessProgressInvoicingAddView(BaseFormView):
    """
    Specific invoice add view
    """

    title = "Nouvelle facture"
    schema = get_new_invoice_schema()

    def submit_success(self, appstruct):
        invoice = self.context.add_progress_invoicing_invoice(
            self.request, self.request.identity
        )
        invoice.name = appstruct.get("name")
        url = self.request.route_path("/invoices/{id}", id=invoice.id)
        return HTTPFound(url)


def business_entry_point_view(context, request):
    """
    Project entry point view only redirects to the most appropriate page
    """
    if context.business_type.label == "default":
        last = request.route_path(PROJECT_ITEM_ROUTE, id=context.project_id)
    else:
        last = request.route_path(BUSINESS_ITEM_OVERVIEW_ROUTE, id=context.id)
    return HTTPFound(last)


def progress_invoicing_url(business, request):
    """
    Build the progress invoicing switch url

    :rtype: str
    """
    return request.route_path(BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE, id=business.id)


def invoice_all_url(business, request):
    """
    Build the url used to generate all invoices

    :rtype: str
    """
    if len(business.payment_deadlines) > 0:
        return request.route_path(
            BUSINESS_ITEM_INVOICING_ALL_ROUTE,
            id=business.id,
        )
    else:
        return None


def get_invoicing_links(business, request):
    """
    Return the appropriate link for invoice generation
    """
    result = []
    if not business.closed:
        # Cas 1 Facturation 'classique'
        if business.invoicing_mode == business.CLASSIC_MODE:
            if business.invoiced:
                label = "Re-générer toutes les factures"
                icon = "file-redo"
            else:
                label = "Générer toutes les factures"
                icon = "file-invoice-euro"
            result.append(
                POSTButton(
                    url=invoice_all_url(business, request), label=label, icon=icon
                )
            )
        else:
            current_invoice = business.get_current_invoice()
            if current_invoice is not None:
                result.append(
                    Link(
                        url=get_task_url(request, current_invoice),
                        label="Terminer la saisie en cours",
                        icon="pen",
                        css="btn icon",
                    )
                )
            else:
                deadlines = business.get_deposit_deadlines(waiting=True)
                if deadlines:
                    for deadline in deadlines:
                        description = "Générer la facture correspondant à "
                        "'Accompte à la commande'"
                        result.append(
                            POSTButton(
                                url=request.route_path(
                                    BUSINESS_ITEM_INVOICING_ROUTE,
                                    id=business.id,
                                    deadline_id=deadline.id,
                                ),
                                label="Générer la facture d’acompte",
                                title=description,
                                icon="file-invoice-euro",
                            )
                        )
                elif not business.progress_invoicing_is_complete():
                    result.append(
                        POSTButton(
                            url=progress_invoicing_url(business, request),
                            label="Générer une nouvelle facture",
                            title="Facture sur le pourcentage d'avancement du projet",
                            icon="file-invoice-euro",
                        )
                    )

    logger.debug("Building invoicing links")
    logger.debug(result)
    return result


class BusinessOverviewView(BaseView, TreeMixin):
    """
    Single business view
    """

    route_name = BUSINESS_ITEM_OVERVIEW_ROUTE

    def __init__(self, *args, **kw):
        BaseView.__init__(self, *args, **kw)

    # Relatif au TreeMixin
    @property
    def tree_is_visible(self):
        """
        Check if this node should be displayed in the breadcrumb tree
        """
        if hasattr(self.context, "project"):
            if not self.context.project.project_type.with_business:
                return False
            elif getattr(self.context, "business_id", "other") is None:
                return False
        return True

    @property
    def title(self):
        """
        Return the page title both for the view and for the breadcrumb
        """
        business = self.current()
        if hasattr(self.context, "business"):
            business = self.context.business
        elif hasattr(self.context, "task"):
            business = self.context.task.business

        return "{0.business_type.label} : {0.name}".format(business)

    @property
    def tree_url(self):
        business = self.current()
        return self.request.route_path(self.route_name, id=business.id)

    def current(self):
        business = self.context
        if hasattr(self.context, "business"):
            business = self.context.business
        elif hasattr(self.context, "task"):
            business = self.context.task.business
        return business

    def estimation_add_url(self):
        """
        Build the estimation add url

        :rtype: str
        """
        return self.request.route_path(
            BUSINESS_ITEM_ESTIMATION_ROUTE, id=self.context.id, _query={"action": "add"}
        )

    def estimation_add_link(self):
        """
        Return A POSTButton for adding estimations
        """
        result = None
        if not self.context.closed:
            label = "Devis complémentaire"
            if not self.context.estimations:
                label = "Devis"
            result = POSTButton(
                url=self.estimation_add_url(),
                label=label,
                title=f"Créer un {label}",
                icon="plus",
            )
        return result

    def switch_invoicing_mode_link(self):
        """
        Build a link used to initialize the business invoicing mode
        """
        result = None
        # Seul les affaires sans factures et avec le droit de faire des études
        # de prix
        if (
            not self.context.invoices
            and self.context.project.project_type.include_price_study
        ):
            url = self.request.route_path(
                BUSINESS_ITEM_ROUTE,
                id=self.context.id,
                _query={"action": "switch_mode"},
            )
            if self.context.invoicing_mode == self.context.CLASSIC_MODE:
                label = "Facturation à l'avancement"
                description = "Utiliser le mode de facturation à l'avancement"
                icon = "steps"
            else:
                label = "Annuler la facturation à l'avancement"
                description = "Revenir à un mode de facturation 'classique'"
                icon = "times"
            result = POSTButton(
                label=label,
                url=url,
                icon=icon,
                title=description,
            )
        return result

    def invoicing_links(self):
        """
        Returns links used for invoicing
        """
        return get_invoicing_links(self.context, self.request)

    def _collect_deadlines(self):
        """
        Collect deadlines we want to present in the UI

        classic invoicing mode : all deadlines
        progress invoicing mode: deposit deadlines
        """
        result = None
        if self.context.invoicing_mode == self.context.CLASSIC_MODE:
            result = self.context.payment_deadlines
        return result

    def _collect_invoice_list(self):
        """
        Collect invoices generated in the current business if in progress
        invoicing mode

        :returns: List of Invoices
        """
        result = None
        if self.context.invoicing_mode == self.context.PROGRESS_MODE:
            result = self.context.invoices
        return result

    def _get_file_tab_link(self):
        return Link(
            self.request.route_path(BUSINESS_ITEM_FILE_ROUTE, id=self.context.id),
            "",
            title="Voir le détail des fichiers",
            icon="arrow-right",
            css="btn icon only",
        )

    def __call__(self):
        """
        Return the context used in the template

        - Invoicing links
        - Deadlines
        - Add estimation link
        - Indicators
        - File requirements
        """
        self.populate_navigation()
        result = dict(
            title=self.title,
            edit_url=self.request.route_path(
                self.route_name, id=self.context.id, _query={"action": "edit"}
            ),
            switch_invoicing_mode_link=self.switch_invoicing_mode_link(),
            invoicing_links=self.invoicing_links(),
            estimations=self.context.estimations,
            custom_indicators=self.context.indicators,
            file_requirements=self.context.get_file_requirements(scoped=False),
            invoice_all_url=invoice_all_url(self.context, self.request),
            payment_deadlines=self._collect_deadlines(),
            invoice_deadline_route=BUSINESS_ITEM_INVOICING_ROUTE,
            estimation_add_link=self.estimation_add_link(),
            # Pour les affaires à l'avancement
            invoice_list=self._collect_invoice_list(),
            file_tab_link=self._get_file_tab_link(),
        )
        return result


class BusinessEditView(BaseEditView, TreeMixin):
    schema = get_business_edit_schema()
    route_name = BUSINESS_ITEM_ROUTE

    @property
    def title(self):
        return "Modification de {0}".format(self.context.name)

    def before(self, form):
        self.populate_navigation()
        return BaseEditView.before(self, form)

    def redirect(self, appstruct):
        return HTTPFound(
            self.request.route_path(BUSINESS_ITEM_ROUTE, id=self.context.id)
        )


class BusinessSwitchInvoicingModeView(BaseView):
    def __call__(self):
        if self.context.project.project_type.include_price_study:
            if self.context.invoicing_mode == self.context.CLASSIC_MODE:
                self.context.set_progress_invoicing_mode()
            else:
                self.context.unset_progress_invoicing_mode()
            self.dbsession.merge(self.context)
        return HTTPFound(
            self.request.route_path(BUSINESS_ITEM_OVERVIEW_ROUTE, id=self.context.id)
        )


def close_business_view(context, request):
    """
    View used to close a Business
    """
    context.closed = True
    request.dbsession.merge(context)
    return HTTPFound(request.route_path(BUSINESS_ITEM_ROUTE, id=context.id))


def includeme(config):
    config.add_view(
        business_entry_point_view,
        route_name=BUSINESS_ITEM_ROUTE,
        permission="view.business",
    )
    config.add_tree_view(
        BusinessOverviewView,
        parent=ProjectEntryPointView,
        renderer="caerp:templates/business/overview.mako",
        permission="view.business",
        layout="business",
    )
    config.add_tree_view(
        BusinessEditView,
        parent=BusinessOverviewView,
        renderer="caerp:templates/base/formpage.mako",
        request_param="action=edit",
        permission="edit.business",
        layout="business",
    )
    config.add_view(
        close_business_view,
        route_name=BUSINESS_ITEM_ROUTE,
        request_param="action=close",
        permission="close.business",
        layout="default",
        request_method="POST",
        require_csrf=True,
    )
    config.add_view(
        BusinessSwitchInvoicingModeView,
        route_name=BUSINESS_ITEM_ROUTE,
        request_param="action=switch_mode",
        layout="business",
        permission="edit.business",
        request_method="POST",
        require_csrf=True,
    )
    config.add_view(
        BusinessProgressInvoicingAddView,
        route_name=BUSINESS_ITEM_PROGRESS_INVOICING_ROUTE,
        layout="business",
        permission="add.business_invoice",
        renderer="caerp:templates/base/formpage.mako",
    )
