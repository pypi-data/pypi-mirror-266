"""
UserDatas add edit views
"""
import logging
from pyramid.httpexceptions import HTTPFound

from deform_extensions import AccordionFormWidget
from js.deform import auto_need
from caerp.models.user.userdatas import (
    UserDatas,
    SocialDocTypeOption,
    UserDatasSocialDocTypes,
    get_default_cae_situation,
)
from caerp.forms.user.userdatas import (
    get_add_edit_schema,
    USERDATAS_FORM_GRIDS,
    get_doctypes_schema,
)
from caerp.utils.strings import (
    format_account,
)
from caerp.utils.menu import (
    AttrMenuDropdown,
)
from caerp.views import (
    BaseFormView,
    BaseEditView,
    submit_btn,
    cancel_btn,
    DeleteView,
)
from caerp.views.user.routes import (
    USER_ITEM_URL,
    USER_ADD_URL,
)
from caerp.views.userdatas.routes import (
    USERDATAS_URL,
    USERDATAS_ITEM_URL,
    USERDATAS_EDIT_URL,
    USERDATAS_DOCTYPES_URL,
    USER_USERDATAS_URL,
    USER_USERDATAS_ADD_URL,
    USER_USERDATAS_EDIT_URL,
    USER_USERDATAS_DOCTYPES_URL,
    USER_USERDATAS_PY3O_URL,
    USER_USERDATAS_CAREER_PATH_URL,
)
from caerp.views.user.tools import UserFormConfigState


logger = logging.getLogger(__name__)


USERDATAS_MENU = AttrMenuDropdown(
    name="userdatas",
    label="Gestion sociale",
    default_route=USER_USERDATAS_URL,
    icon="address-card",
    hidden_attribute="userdatas",
    perm="edit.userdatas",
)
USERDATAS_MENU.add_item(
    name="userdatas_view",
    label="Fiche du porteur",
    route_name=USER_USERDATAS_EDIT_URL,
    icon="user-circle",
    perm="view.userdatas",
)
USERDATAS_MENU.add_item(
    name="userdatas_parcours",
    label="Parcours",
    route_name=USER_USERDATAS_CAREER_PATH_URL,
    other_route_name="career_path",
    icon="chart-line",
    perm="view.userdatas",
)
USERDATAS_MENU.add_item(
    name="userdatas_doctypes",
    label="Documents sociaux",
    route_name=USER_USERDATAS_DOCTYPES_URL,
    icon="check-square",
    perm="doctypes.userdatas",
)
USERDATAS_MENU.add_item(
    name="userdatas_py3o",
    label="Génération de documents",
    route_name=USER_USERDATAS_PY3O_URL,
    icon="file-alt",
    perm="py3o.userdatas",
)


def userdatas_add_entry_point(context, request):
    """
    Entry point for userdatas add
    Record the userdatas form as next form urls

    The add process follows this stream :
        1- entry point
        2- user add form
        3- userdatas form
    """
    config = UserFormConfigState(request.session)
    config.set_steps([USER_USERDATAS_ADD_URL])
    config.set_defaults({"primary_group": "contractor"})
    return HTTPFound(request.route_path(USER_ADD_URL))


def userdatas_add_view(context, request):
    """
    Add userdatas to an existing User object

    :param obj context: The pyramid context (User instance)
    :param obj request: The pyramid request
    """
    logger.debug("Adding userdatas for the user %s" % context.id)
    user_datas = UserDatas()
    user_datas.user_id = context.id
    user_datas.coordonnees_civilite = context.civilite
    user_datas.coordonnees_lastname = context.lastname
    user_datas.coordonnees_firstname = context.firstname
    user_datas.coordonnees_email1 = context.email
    user_datas.situation_situation_id = get_default_cae_situation()
    request.dbsession.add(user_datas)
    request.dbsession.flush()
    return HTTPFound(
        request.route_path(
            USER_USERDATAS_EDIT_URL,
            id=context.id,
        )
    )


def ensure_doctypes_rel(userdatas_id, request):
    """
    Ensure there is a UserDatasSocialDocTypes instance attaching each social doc
    type with the userdatas

    :param int userdatas_id: The id of the userdatas instance
    :param obj request: The request object
    """
    for doctype in SocialDocTypeOption.query():
        doctype_id = doctype.id
        rel = UserDatasSocialDocTypes.get(
            (
                userdatas_id,
                doctype_id,
            )
        )
        if rel is None:
            rel = UserDatasSocialDocTypes(
                userdatas_id=userdatas_id,
                doctype_id=doctype_id,
            )
            request.dbsession.add(rel)
    request.dbsession.flush()


class UserDatasEditView(BaseEditView):
    """
    User datas edition view
    """

    buttons = (
        submit_btn,
        cancel_btn,
    )
    add_template_vars = ("current_userdatas", "delete_url")

    @property
    def title(self):
        return "Fiche de gestion sociale de {0}".format(
            format_account(self.current_userdatas.user, False)
        )

    @property
    def current_userdatas(self):
        return self.context

    @property
    def delete_url(self):
        return self.request.route_path(
            USERDATAS_ITEM_URL,
            id=self.current_userdatas.id,
            _query={"action": "delete"},
        )

    def get_schema(self):
        return get_add_edit_schema()

    def before(self, form):
        BaseEditView.before(self, form)
        auto_need(form)
        form.widget = AccordionFormWidget(
            named_grids=USERDATAS_FORM_GRIDS, fallback_down=True
        )

    def get_context_model(self):
        return self.current_userdatas

    def redirect(self, appstruct):
        return HTTPFound(self.request.current_route_path())


class UserUserDatasEditView(UserDatasEditView):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class UserDatasDeleteView(DeleteView):
    def redirect(self):
        return HTTPFound(
            self.request.route_path(USER_ITEM_URL, id=self.context.user_id)
        )


class UserDatasDocTypeView(BaseFormView):
    _schema = None
    title = "Liste des documents fournis par l'entrepreneur"
    form_options = (("formid", "doctypes-form"),)
    add_template_vars = ("current_userdatas", "is_void")

    def __init__(self, *args, **kwargs):
        BaseFormView.__init__(self, *args, **kwargs)
        ensure_doctypes_rel(self.current_userdatas.id, self.request)

    @property
    def current_userdatas(self):
        return self.context

    @property
    def schema(self):
        if self._schema is None:
            self._schema = get_doctypes_schema(self.current_userdatas)

        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    def before(self, form):
        appstruct = {}
        for index, entry in enumerate(self.current_userdatas.doctypes_registrations):
            appstruct["node_%s" % index] = {
                "userdatas_id": entry.userdatas_id,
                "doctype_id": entry.doctype_id,
                "status": entry.status,
            }
        form.set_appstruct(appstruct)
        return form

    @property
    def is_void(self):
        return not self.schema.children

    def submit_success(self, appstruct):
        node_schema = self.schema.children[0]
        for key, value in list(appstruct.items()):
            logger.debug(value)
            model = node_schema.objectify(value)
            self.dbsession.merge(model)

        self.request.session.flash("Vos modifications ont été enregistrées")

        return HTTPFound(self.request.current_route_path())


class UserUserDatasDocTypeView(UserDatasDocTypeView):
    @property
    def current_userdatas(self):
        return self.context.userdatas


def add_views(config):
    """
    Add module related views
    """
    config.add_view(
        userdatas_add_view,
        route_name=USER_USERDATAS_ADD_URL,
        permission="add.userdatas",
        # request_method="POST",
        # require_csrf=True,
    )
    config.add_view(
        UserDatasEditView,
        route_name=USERDATAS_EDIT_URL,
        permission="edit.userdatas",
        renderer="/base/formpage.mako",
    )
    config.add_view(
        UserUserDatasEditView,
        route_name=USER_USERDATAS_URL,
        permission="edit.userdatas",
        renderer="/userdatas/edit.mako",
        layout="user",
    )
    config.add_view(
        UserUserDatasEditView,
        route_name=USER_USERDATAS_EDIT_URL,
        permission="edit.userdatas",
        renderer="/userdatas/edit.mako",
        layout="user",
    )
    config.add_view(
        UserDatasDeleteView,
        route_name=USERDATAS_ITEM_URL,
        permission="delete.userdatas",
        request_param="action=delete",
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        userdatas_add_entry_point,
        route_name=USERDATAS_URL,
        request_param="action=add",
        permission="add.userdatas",
    )
    config.add_view(
        UserDatasDocTypeView,
        route_name=USERDATAS_DOCTYPES_URL,
        permission="doctypes.userdatas",
        renderer="/base/formpage.mako",
    )
    config.add_view(
        UserUserDatasDocTypeView,
        route_name=USER_USERDATAS_DOCTYPES_URL,
        permission="doctypes.userdatas",
        renderer="/userdatas/doctypes.mako",
        layout="user",
    )


def register_menus():
    from caerp.views.user.layout import UserMenu

    UserMenu.add_after("companies", USERDATAS_MENU)


def includeme(config):
    """
    Pyramid main entry point

    :param obj config: The current application config object
    """
    add_views(config)
    register_menus()
