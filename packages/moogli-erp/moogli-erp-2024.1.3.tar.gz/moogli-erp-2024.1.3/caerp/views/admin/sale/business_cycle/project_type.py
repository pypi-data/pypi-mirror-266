import os
from pyramid.httpexceptions import HTTPFound

from caerp.models.project.types import (
    ProjectType,
    BusinessType,
)

from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.forms.admin.sale.business_cycle.project_type import (
    get_admin_project_type_schema,
    get_admin_business_type_schema,
)
from caerp.views import (
    BaseView,
)
from caerp.views.admin.tools import (
    AdminCrudListView,
    BaseAdminDisableView,
    BaseAdminDeleteView,
    BaseAdminEditView,
    BaseAdminAddView,
)

from caerp.views.admin.sale.business_cycle import BusinessCycleIndexView, BUSINESS_URL

PROJECT_TYPE_URL = os.path.join(BUSINESS_URL, "project_types")
PROJECT_TYPE_ITEM_URL = os.path.join(PROJECT_TYPE_URL, "{id}")
BUSINESS_TYPE_URL = os.path.join(BUSINESS_URL, "business_types")
BUSINESS_TYPE_ITEM_URL = os.path.join(BUSINESS_TYPE_URL, "{id}")


class ProjectTypeListView(AdminCrudListView):
    title = "Types de dossier"
    description = "Configurer les types de dossier proposés aux entrepreneurs \
ceux-ci servent de base pour la configuration des cycles d'affaire."
    route_name = PROJECT_TYPE_URL
    item_route_name = PROJECT_TYPE_ITEM_URL
    columns = [
        "Libellé",
        "Nécessite des droits particuliers",
        "Type de dossier par défaut",
        "Permet les études de prix",
        "Mode(s) de saisie des prix",
    ]
    factory = ProjectType

    def stream_columns(self, type_):
        check_mark = "<span class='icon'>\
            <svg><use href='{}#check'></use></svg>\
            </span>".format(
            self.request.static_url("caerp:static/icons/endi.svg")
        )
        yield type_.label
        if type_.private:
            yield check_mark
        else:
            yield ""
        if type_.default:
            yield "{}<br />Type par défaut".format(check_mark)
        else:
            yield ""

        if type_.include_price_study:
            yield check_mark
        else:
            yield ""

        compute_modes = []
        if type_.ht_compute_mode_allowed:
            compute_modes.append("HT")
        if type_.ttc_compute_mode_allowed:
            compute_modes.append("TTC")
        yield "/".join(compute_modes)

    def stream_actions(self, type_):
        yield Link(
            self._get_item_url(type_), "Voir ou modifier", icon="pen", css="icon"
        )
        if type_.active:
            yield POSTButton(
                self._get_item_url(type_, action="disable"),
                "Désactiver",
                title="Ce type de dossier ne sera plus proposé aux utilisateurs",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(type_, action="disable"),
                "Activer",
                title="Ce type de dossier sera proposé aux utilisateurs",
                icon="lock-open",
                css="icon",
            )

        if not type_.default:
            yield POSTButton(
                self._get_item_url(type_, action="set_default"),
                label="Définir comme type par défaut",
                title="Le type sera sélectionné par défaut à la création "
                "d'un dossier",
                icon="check",
                css="icon",
            )

        if not type_.is_used():
            yield POSTButton(
                self._get_item_url(type_, action="delete"),
                "Supprimer",
                title="Supprimer ce type de dossier",
                icon="trash-alt",
                confirm="Êtes-vous sûr de vouloir supprimer cet élément ?",
                css="icon negative",
            )

    def load_items(self):
        """
        Return the sqlalchemy models representing current queried elements
        :rtype: SQLAlchemy.Query object
        """
        items = ProjectType.query()
        items = items.order_by(self.factory.default).order_by(self.factory.name)
        return items


class ProjectTypeDisableView(BaseAdminDisableView):
    """
    View for ProjectType disable/enable
    """

    route_name = PROJECT_TYPE_ITEM_URL


class ProjectTypeDeleteView(BaseAdminDeleteView):
    """
    ProjectType deletion view
    """

    route_name = PROJECT_TYPE_ITEM_URL


class ProjectTypeAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = PROJECT_TYPE_URL
    factory = ProjectType
    schema = get_admin_project_type_schema()


class ProjectTypeEditView(BaseAdminEditView):
    route_name = PROJECT_TYPE_ITEM_URL
    factory = ProjectType
    schema = get_admin_project_type_schema()

    @property
    def title(self):
        return "Modifier le type de dossier '{0}'".format(self.context.label)


class ProjectTypeSetDefaultView(BaseView):
    """
    Set the given tva as default
    """

    route_name = PROJECT_TYPE_ITEM_URL

    def __call__(self):
        for item in ProjectType.query():
            item.default = False
            self.request.dbsession.merge(item)
        self.context.default = True
        self.request.dbsession.merge(item)
        return HTTPFound(
            self.request.route_path(
                PROJECT_TYPE_URL,
            )
        )


class BusinessTypeListView(AdminCrudListView):
    title = "Types d'affaire"
    description = """Configurer les types d'affaires proposés aux
    entrepreneurs. Les types d'affaire permettent de spécifier des règles
    (documents requis ...) spécifiques.
    """
    factory = BusinessType
    route_name = BUSINESS_TYPE_URL
    item_route_name = BUSINESS_TYPE_ITEM_URL
    columns = [
        "Libellé",
        "Nécessite des droits particuliers",
        "Par défaut pour les dossiers de type",
        "Sélectionnable pour les dossiers de type",
        "Inscrit au BPF",
        "TVA sur marge",
    ]

    def stream_columns(self, type_):
        check_mark = "<span class='icon'>\
            <svg><use href='{}#check'></use></svg>\
            </span>".format(
            self.request.static_url("caerp:static/icons/endi.svg")
        )
        yield type_.label
        if type_.private:
            yield check_mark
        else:
            yield ""
        if type_.project_type:
            yield type_.project_type.label
        else:
            yield ""

        yield ",".join([t.label for t in type_.other_project_types])
        yield check_mark if type_.bpf_related else ""
        yield check_mark if type_.tva_on_margin else ""

    def stream_actions(self, type_):
        # if type_.editable:
        yield Link(self._get_item_url(type_), "Voir/Modifier", icon="pen", css="icon")
        if type_.active:
            yield POSTButton(
                self._get_item_url(type_, action="disable"),
                "Désactiver",
                title="Ce type d'affaire ne sera plus proposé aux " "utilisateurs",
                icon="lock",
                css="icon",
            )
        else:
            yield POSTButton(
                self._get_item_url(type_, action="disable"),
                "Activer",
                title="Ce type d'affaire sera proposé aux utilisateurs",
                icon="lock-open",
                css="icon",
            )

        if not type_.is_used():
            yield POSTButton(
                self._get_item_url(type_, action="delete"),
                "Supprimer",
                title="Supprimer ce type d'affaire",
                icon="trash-alt",
                confirm="Êtes-vous sûr de vouloir supprimer cet élément ?",
                css="icon negative",
            )

    def load_items(self):
        items = BusinessType.query()
        items = items.order_by(self.factory.name)
        return items


class BusinessTypeDisableView(BaseAdminDisableView):
    """
    View for BusinessType disable/enable
    """

    route_name = BUSINESS_TYPE_ITEM_URL


class BusinessTypeDeleteView(BaseAdminDeleteView):
    """
    BusinessType deletion view
    """

    route_name = BUSINESS_TYPE_ITEM_URL


class BusinessTypeAddView(BaseAdminAddView):
    title = "Ajouter"
    route_name = BUSINESS_TYPE_URL
    factory = BusinessType
    schema = get_admin_business_type_schema(edit=False)


class BusinessTypeEditView(BaseAdminEditView):
    route_name = BUSINESS_TYPE_ITEM_URL
    factory = BusinessType
    schema = get_admin_business_type_schema(edit=True)

    @property
    def title(self):
        return "Modifier le type d'affaire '{0}'".format(self.context.label)


def includeme(config):
    config.add_route(PROJECT_TYPE_URL, PROJECT_TYPE_URL)
    config.add_route(
        PROJECT_TYPE_ITEM_URL, PROJECT_TYPE_ITEM_URL, traverse="/project_types/{id}"
    )
    config.add_route(BUSINESS_TYPE_URL, BUSINESS_TYPE_URL)
    config.add_route(
        BUSINESS_TYPE_ITEM_URL, BUSINESS_TYPE_ITEM_URL, traverse="/business_types/{id}"
    )

    config.add_admin_view(
        ProjectTypeListView,
        parent=BusinessCycleIndexView,
        renderer="admin/crud_list.mako",
    )

    config.add_admin_view(
        ProjectTypeAddView,
        parent=ProjectTypeListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        ProjectTypeEditView,
        parent=ProjectTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        ProjectTypeDisableView,
        parent=ProjectTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        ProjectTypeDeleteView,
        parent=ProjectTypeListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        ProjectTypeSetDefaultView,
        request_param="action=set_default",
        request_method="POST",
        require_csrf=True,
    )

    config.add_admin_view(
        BusinessTypeListView,
        parent=BusinessCycleIndexView,
        renderer="admin/crud_list.mako",
    )

    config.add_admin_view(
        BusinessTypeAddView,
        parent=BusinessTypeListView,
        renderer="admin/crud_add_edit.mako",
        request_param="action=add",
    )
    config.add_admin_view(
        BusinessTypeEditView,
        parent=BusinessTypeListView,
        renderer="admin/crud_add_edit.mako",
    )
    config.add_admin_view(
        BusinessTypeDisableView,
        parent=BusinessTypeListView,
        request_param="action=disable",
        request_method="POST",
        require_csrf=True,
    )
    config.add_admin_view(
        BusinessTypeDeleteView,
        parent=BusinessTypeListView,
        request_param="action=delete",
        request_method="POST",
        require_csrf=True,
    )
