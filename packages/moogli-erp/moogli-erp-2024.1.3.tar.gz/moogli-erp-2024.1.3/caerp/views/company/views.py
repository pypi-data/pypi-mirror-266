from collections import namedtuple
import logging
from typing import Dict

import colander

from deform_extensions import AccordionFormWidget
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from caerp.models.company import Company
from caerp.models.user.user import User
from caerp.utils.widgets import (
    ViewLink,
    Link,
    POSTButton,
)

from caerp.views import (
    BaseAddView,
    BaseEditView,
    BaseView,
    submit_btn,
    add_panel_view,
    DisableView,
    JsAppViewMixin,
)
from caerp.views.render_api import format_account
from caerp.views.user.routes import (
    USER_LOGIN_URL,
    USER_URL,
)
from caerp.views.files.routes import FILE_PNG_ITEM
from caerp.forms.company import (
    get_company_schema,
    COMPANY_FORM_GRID,
)
from caerp.resources import (
    dashboard_resources,
    node_view_only_js,
)

from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule

from .tools import get_company_url

from .routes import (
    COLLECTION_ROUTE,
    ITEM_ROUTE,
    DASHBOARD_ROUTE,
    COMPANY_ESTIMATION_ADD_ROUTE,
    COMPANY_INVOICE_ADD_ROUTE,
)


logger = logging.getLogger(__name__)


ENABLE_MSG = "L'enseigne {0} a été (ré)activée."
DISABLE_MSG = "L'enseigne {0} a été désactivée."

ENABLE_ERR_MSG = "Erreur à l'activation de l'enseigne {0}."
DISABLE_ERR_MSG = "Erreur à la désactivation de l'enseigne {0}."
PUBLIC_DATA_INFO = """
  Les <em>Informations publiques</em> apparaissent sur les devis/factures,
  dans l'annuaire des entrepreneurs,
  et peuvent être publiées à l'extérieur de la CAE.
"""


ShortcutButton = namedtuple("ShortcutButton", ["url", "icon", "text", "title"])


def get_enabled_bookeeping_modules() -> dict:
    """
    List enabled bookeeping modules
    """
    enabled_modules = {}
    for prefix in ("", "internal"):
        for module in ("contribution", "insurance"):
            key = "{}{}".format(prefix, module)
            enabled_modules[key] = (
                CustomInvoiceBookEntryModule.get_by_name(module, prefix) is not None
            )
    return enabled_modules


def _get_company_shortcuts(company, request) -> dict:
    """
    Collect shortcuts for the company dashboard
    """
    buttons = []
    msg = ""
    if company.customers:
        if company.projects:
            buttons.append(
                ShortcutButton(
                    url=request.route_path(
                        COMPANY_ESTIMATION_ADD_ROUTE,
                        id=company.id,
                    ),
                    icon="file-list",
                    text="Créer un devis",
                    title="Créer un nouveau devis",
                )
            )
            if request.has_permission("add.invoice", company):
                buttons.append(
                    ShortcutButton(
                        url=request.route_path(
                            COMPANY_INVOICE_ADD_ROUTE,
                            id=company.id,
                        ),
                        icon="file-invoice-euro",
                        text="Créer une facture",
                        title="Créer une nouvelle facture",
                    )
                )
        else:
            msg = "Ajoutez un dossier qui contiendra des devis et factures"
    else:
        msg = "Pour commencer, ajoutez un client"

    if len(company.employees) == 1 or request.identity in company.employees:
        if request.identity in company.employees:
            expense_user = request.identity
        else:
            # EA externe à l'enseigne
            expense_user = company.employees[0]

        buttons.append(
            ShortcutButton(
                url=request.route_path(
                    "user_expenses",
                    id=company.id,
                    uid=expense_user.id,
                ),
                icon="credit-card",
                text="Créer une note de dépense",
                title="Créer une nouvelle note de dépense",
            )
        ),
    # EA externe + multi-employés : on affiche pas le bouton.

    if company.customers:
        buttons.append(
            ShortcutButton(
                url=request.route_path(
                    "/companies/{id}/projects",
                    id=company.id,
                    _query=dict(action="add"),
                ),
                icon="folder",
                text="Ajouter un dossier",
                title="Ajouter un nouveau dossier",
            )
        )

    # Ref https://framagit.org/caerp/caerp/-/issues/2485
    # buttons.append(ShortcutButton(
    #     url=request.route_path(
    #         'company_customers',
    #         id=company.id,
    #         _query=dict(action='add'),
    #     ),
    #     icon='user',
    #     text="Ajouter un client",
    #     title="Ajouter un nouveau client",
    # ))
    return dict(
        shortcuts_msg=msg,
        shortucts_buttons=buttons,
    )


def company_dashboard(request):
    """
    index page for the company shows latest news :
        - last validated estimation/invoice
        - To be relaunched bill
        - shortcut buttons
    """
    dashboard_resources.need()
    company = request.context

    shortcuts = _get_company_shortcuts(company, request)

    ret_val = dict(
        title=company.name.title(),
        company=company,
        elapsed_invoices=request.context.get_late_invoices(),
    )
    ret_val.update(shortcuts)
    return ret_val


class CompanyView(JsAppViewMixin, BaseView):
    def context_url(self, _query: Dict[str, str] = {}):
        return get_company_url(self.request, api=True, **_query)

    def __call__(self):
        context = self.context
        request = self.request
        company = request.context

        populate_actionmenu(request)
        node_view_only_js.need()

        actions = []
        if request.has_permission("edit_company"):
            actions.append(
                Link(
                    get_company_url(request, action="edit"),
                    "Modifier",
                    title="Modifier l´enseigne",
                    icon="pen",
                    css="btn btn-primary icon",
                )
            )

        if request.has_permission("admin_company"):
            url = get_company_url(request, action="disable")
            if company.active:
                actions.append(
                    POSTButton(
                        url,
                        "Désactiver",
                        title="Désactiver l'enseigne",
                        icon="lock",
                        css="icon",
                    )
                )
            else:
                actions.append(
                    POSTButton(
                        url,
                        "Activer",
                        title="Activer l'enseigne",
                        icon="lock-open",
                        css="icon",
                    )
                )

        return dict(
            title=company.name.title(),
            company=company,
            actions=actions,
            enabled_modules=get_enabled_bookeeping_modules(),
            js_app_options=self.get_js_app_options(),
        )


class CompanyDisableView(DisableView):
    def on_disable(self):
        """
        Disable logins of users that are only attached to this company
        """
        for user in self.context.employees:
            other_enabled_companies = [
                company
                for company in user.companies
                if company.active and company.id != self.context.id
            ]
            if (
                getattr(user, "login")
                and user.login.active
                and len(other_enabled_companies) == 0
            ):
                user.login.active = False
                self.request.dbsession.merge(user.login)
                user_url = self.request.route_path(USER_LOGIN_URL, id=user.id)
                self.request.session.flash(
                    "Les identifiants de <a href='{0}'>{1}</a> ont été        "
                    "             désactivés".format(user_url, user.label)
                )

    def redirect(self):
        return HTTPFound(self.request.referrer)


def set_company_image(company, appstruct):
    for fname in ("header", "logo"):
        if fname in appstruct:
            setattr(company, fname, appstruct.get(fname, {}))


class CompanyAdd(BaseAddView):
    """
    View class for company add

    Have support for a user_id request param that allows to add the user
    directly on company creation

    """

    add_template_vars = ("title",)
    title = "Ajouter une enseigne"
    buttons = (submit_btn,)
    msg = "L'enseigne a bien été ajoutée"
    factory = Company

    def get_schema(self) -> colander.SchemaNode:
        """
        Renvoie un schéma dynamiquement généré
        """
        modules = get_enabled_bookeeping_modules()
        admin = bool(self.request.has_permission("admin_treasury"))
        schema = get_company_schema(
            admin=admin,
            excludes=[key for key, value in modules.items() if not value],
        )
        return schema

    def before(self, form):
        """
        prepopulate the form and the actionmenu
        """
        populate_actionmenu(self.request)
        form.widget = AccordionFormWidget(named_grids=COMPANY_FORM_GRID)

        if "user_id" in self.request.params:
            appstruct = {"user_id": self.request.params["user_id"]}

            come_from = self.request.referrer
            if come_from:
                appstruct["come_from"] = come_from

            form.set_appstruct(appstruct)

    def on_add(self, company, appstruct):
        self.come_from = appstruct.pop("come_from", None)
        user_id = appstruct.pop("user_id", None)
        if user_id is not None:
            user_account = User.get(user_id)
            if user_account is not None:
                company.employees.append(user_account)
                company.set_datas_from_user(user_account)
        set_company_image(company, appstruct)

    def redirect(self, appstruct, company):
        if getattr(self, "come_from", None) is not None:
            return HTTPFound(self.come_from)
        else:
            return HTTPFound(get_company_url(self.request, company))


class CompanyEdit(BaseEditView):
    """
    View class for company editing
    """

    add_template_vars = ("title", "info_message")
    buttons = (submit_btn,)
    info_message = PUBLIC_DATA_INFO

    def get_schema(self):
        modules = get_enabled_bookeeping_modules()
        admin = bool(self.request.has_permission("admin_treasury"))
        schema = get_company_schema(
            admin=admin,
            excludes=[key for key, value in modules.items() if not value],
        )
        return schema

    @reify
    def title(self):
        """
        title property
        """
        return "Modification de {0}".format(self.context.name.title())

    def before(self, form):
        super(CompanyEdit, self).before(form)
        appstruct = self.schema.dictify(self.context)

        for filetype in ("logo", "header"):
            # On récupère un éventuel id de fichier
            file_id = getattr(self.context, "{}_id".format(filetype))
            if file_id:
                # Si il y a déjà un fichier de ce type dans la base on
                # construit un appstruct avec un uid, un filename et une url de
                # preview
                fileobject = getattr(self.context, filetype)
                appstruct[filetype] = {
                    "uid": fileobject.name,
                    "filename": fileobject.name,
                    "preview_url": self.request.route_path(
                        FILE_PNG_ITEM,
                        id=file_id,
                    ),
                }
        form.set_appstruct(appstruct)
        form.widget = AccordionFormWidget(named_grids=COMPANY_FORM_GRID)
        populate_actionmenu(self.request, self.context)
        self.old_general_overhead = self.context.general_overhead
        self.old_margin_rate = self.context.margin_rate

    def on_edit(self, appstruct, model):
        """
        Edit the database entry and return redirect
        """
        logger.debug("New company attributes : {}".format(appstruct))
        set_company_image(model, appstruct)
        self.dbsession.flush()

        # Clear all informations stored in session by the tempstore used for
        # the file upload widget
        self.session.pop("substanced.tempstore")
        self.session.changed()

    def redirect(self, appstruct):
        return HTTPFound(get_company_url(self.request))


def populate_actionmenu(request, company=None):
    """
    add item in the action menu
    """
    request.actionmenu.add(get_list_view_btn())
    if company is not None:
        request.actionmenu.add(get_view_btn(company.id))


def get_list_view_btn():
    """
    Return a link to the CAE's directory
    """
    return ViewLink("Annuaire", "visit", path=USER_URL)


def get_view_btn(company_id):
    """
    Return a link to the view page
    """
    return ViewLink("Fiche de l’enseigne", "visit", path=ITEM_ROUTE, id=company_id)


def company_remove_employee_view(context, request):
    """
    Enlève un employé de l'enseigne courante
    """
    uid = request.params.get("uid")
    if not uid:
        request.session.flash("Missing uid parameter", "error")
    else:
        user = User.get(uid)
        if not user:
            request.session.flash("User not found", "error")

        if user in context.employees:
            context.employees = [
                employee for employee in context.employees if employee != user
            ]
            request.session.flash(
                "L'utilisateur {0} ne fait plus partie de l'enseigne {1}".format(
                    format_account(user), context.name
                )
            )
    url = request.referer
    if url is None:
        url = get_company_url(request)
    return HTTPFound(url)


def includeme(config):
    config.add_view(
        CompanyAdd,
        route_name=COLLECTION_ROUTE,
        renderer="base/formpage.mako",
        request_param="action=add",
        permission="admin_companies",
    )
    config.add_view(
        company_dashboard,
        route_name=DASHBOARD_ROUTE,
        renderer="company_index.mako",
        permission="view.company",
    )
    config.add_view(
        company_dashboard,
        route_name=ITEM_ROUTE,
        renderer="company_index.mako",
        request_param="action=index",
        permission="view.company",
    )
    config.add_view(
        CompanyView,
        route_name=ITEM_ROUTE,
        renderer="company.mako",
        permission="visit",
    )
    config.add_view(
        CompanyEdit,
        route_name=ITEM_ROUTE,
        renderer="base/formpage.mako",
        request_param="action=edit",
        permission="edit_company",
    )
    config.add_view(
        CompanyDisableView,
        route_name=ITEM_ROUTE,
        request_param="action=disable",
        permission="admin_company",
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        company_remove_employee_view,
        route_name=ITEM_ROUTE,
        request_param="action=remove",
        permission="admin_company",
        require_csrf=True,
        request_method="POST",
    )
    # same panel as html view
    for panel, request_param in (
        (
            "company_recent_tasks",
            "action=tasks_html",
        ),
        (
            "company_coming_events",
            "action=events_html",
        ),
    ):
        add_panel_view(
            config,
            panel,
            route_name=ITEM_ROUTE,
            request_param=request_param,
            permission="view.company",
        )
