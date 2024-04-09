import logging
from sqlalchemy.orm import load_only

from pyramid.httpexceptions import HTTPFound
from deform_extensions import AccordionFormWidget
from js.deform import auto_need

from caerp.utils.strings import (
    format_account,
)
from caerp.models import files
from caerp.models.training.trainer import TrainerDatas
from caerp.forms.training.trainer import (
    get_add_edit_trainerdatas_schema,
    FORM_GRID,
)
from caerp.utils.menu import AttrMenuDropdown
from caerp.views import (
    BaseView,
    BaseEditView,
    DeleteView,
    submit_btn,
    cancel_btn,
)
from caerp.views.files.views import (
    FileUploadView,
)
from caerp.views.user.routes import (
    USER_ITEM_URL,
)
from caerp.views.training.routes import (
    TRAINER_ITEM_URL,
    TRAINER_FILE_URL,
    USER_TRAINER_URL,
    USER_TRAINER_EDIT_URL,
    USER_TRAINER_FILE_URL,
    USER_TRAINER_ADD_URL,
)


logger = logging.getLogger(__name__)

TRAINER_MENU = AttrMenuDropdown(
    name="trainerdatas",
    label="Formation",
    default_route=USER_TRAINER_URL,
    icon="chalkboard-teacher",
    hidden_attribute="trainerdatas",
    perm="view.trainerdatas",
)
TRAINER_MENU.add_item(
    name="trainerdatas_view",
    label="Fiche formateur",
    route_name=USER_TRAINER_EDIT_URL,
    icon="user-circle",
    perm="edit.trainerdatas",
)
TRAINER_MENU.add_item(
    name="trainerdatas_filelist",
    label="Fichiers liés au formateur",
    route_name=USER_TRAINER_FILE_URL,
    icon="folder",
    perm="filelist.trainerdatas",
)


def trainerdatas_add_entry_view(context, request):
    """
    Trainer datas add view

    :param obj context: The pyramid context (User instance)
    :param obj request: The pyramid request
    """
    logger.debug("Adding Trainer datas for the user %s" % context.id)
    trainerdatas = TrainerDatas(user_id=context.id)
    request.dbsession.add(trainerdatas)
    request.dbsession.flush()
    if context.login is not None:
        context.login.groups.append("trainer")
        request.dbsession.merge(context.login)
    return HTTPFound(
        request.route_path(
            USER_TRAINER_EDIT_URL,
            id=context.id,
        )
    )


class TrainerDatasEditView(BaseEditView):
    """
    Trainer datas edition view
    """

    schema = get_add_edit_trainerdatas_schema()
    buttons = (
        submit_btn,
        cancel_btn,
    )
    add_template_vars = ("delete_url", "current_trainerdatas")

    @property
    def delete_url(self):
        return self.request.route_path(
            TRAINER_ITEM_URL,
            id=self.current_trainerdatas.id,
            _query={"action": "delete"},
        )

    @property
    def title(self):
        return "Fiche formateur de {0}".format(
            format_account(self.current_trainerdatas.user)
        )

    @property
    def current_trainerdatas(self):
        return self.context

    def before(self, form):
        BaseEditView.before(self, form)
        auto_need(form)
        form.widget = AccordionFormWidget(named_grids=FORM_GRID)

    def get_context_model(self):
        return self.current_trainerdatas

    def redirect(self, appstruct):
        return HTTPFound(self.request.current_route_path())


class UserTrainerDatasEditView(TrainerDatasEditView):
    @property
    def current_trainerdatas(self):
        return self.context.trainerdatas


class TrainerDatasDeleteView(DeleteView):
    """
    TrainerDatas deletion view
    """

    delete_msg = "La fiche formateur a bien été supprimée"

    def on_delete(self):
        login = self.context.user.login
        if login is not None:
            if "trainer" in login.groups:
                login.groups.remove("trainer")
                self.request.dbsession.merge(login)

    def redirect(self):
        return HTTPFound(
            self.request.route_path(USER_ITEM_URL, id=self.context.user_id)
        )


class TrainerDatasFileAddView(FileUploadView):
    factory = files.File
    title = "Attacher un fichier à la fiche formateur de l’entrepreneur"


class TrainerDatasFileList(BaseView):
    @property
    def current_trainerdatas(self):
        return self.context

    def _get_add_url(self):
        """
        Build the url to the file add view
        """
        return self.request.route_path(
            TRAINER_FILE_URL,
            id=self.current_trainerdatas.id,
            _query=dict(action="attach_file"),
        )

    def __call__(self):
        query = files.File.query().options(
            load_only(
                "description",
                "name",
                "updated_at",
                "id",
            )
        )
        query = query.filter_by(parent_id=self.current_trainerdatas.id)

        return dict(
            title="Documents formateur",
            files=query,
            current_trainerdatas=self.current_trainerdatas,
            add_url=self._get_add_url(),
            help_message="Liste des documents liés au statut de formateur "
            "de l’entrepreneur. Ces documents sont visibles par "
            "l’entrepreneur.",
        )


class UserTrainerDatasFileList(TrainerDatasFileList):
    @property
    def current_trainerdatas(self):
        return self.context.trainerdatas


def add_views(config):
    config.add_view(
        trainerdatas_add_entry_view,
        route_name=USER_TRAINER_ADD_URL,
        permission="add.trainerdatas",
        request_method="POST",
        require_csrf=True,
    )
    config.add_view(
        TrainerDatasEditView,
        route_name=TRAINER_ITEM_URL,
        permission="edit.trainerdatas",
        renderer="caerp:templates/training/trainerdatas_edit.mako",
        layout="user",
    )
    config.add_view(
        UserTrainerDatasEditView,
        route_name=USER_TRAINER_EDIT_URL,
        permission="edit.trainerdatas",
        renderer="caerp:templates/training/trainerdatas_edit.mako",
        layout="user",
    )
    config.add_view(
        UserTrainerDatasFileList,
        route_name=USER_TRAINER_FILE_URL,
        permission="filelist.trainerdatas",
        renderer="caerp:templates/training/filelist.mako",
        layout="user",
    )
    config.add_view(
        TrainerDatasFileList,
        route_name=TRAINER_FILE_URL,
        permission="filelist.trainerdatas",
        renderer="caerp:templates/training/filelist.mako",
        layout="user",
    )
    config.add_view(
        TrainerDatasFileAddView,
        route_name=TRAINER_FILE_URL,
        permission="addfile.trainerdatas",
        request_param="action=attach_file",
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
    )

    config.add_view(
        TrainerDatasDeleteView,
        route_name=TRAINER_ITEM_URL,
        permission="delete.trainerdatas",
        request_param="action=delete",
        layout="default",
        request_method="POST",
        require_csrf=True,
    )


def register_menus():
    from caerp.views.user.layout import UserMenu

    UserMenu.add(TRAINER_MENU)


def includeme(config):
    """
    Pyramid main entry point

    :param obj config: The current application config object
    """
    add_views(config)
    register_menus()
    config.add_admin_menu(
        parent="training",
        order=2,
        href="/trainers",
        label="Annuaire des formateurs",
    )
