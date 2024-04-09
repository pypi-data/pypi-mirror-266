from sqlalchemy.orm import load_only
from caerp.models import files
from caerp.forms.files import UserDatasFileUploadSchema
from caerp.views import BaseView
from caerp.views.files.views import FileUploadView, FileEditView
from caerp.views.userdatas.userdatas import USERDATAS_MENU
from caerp.views.userdatas.routes import (
    USERDATAS_FILELIST_URL,
    USERDATAS_ITEM_URL,
    USER_USERDATAS_FILELIST_URL,
    USER_USERDATAS_MYDOCUMENTS_URL,
)


USERDATAS_MENU.add_item(
    name="userdatas_filelist",
    label="Portefeuille de documents",
    route_name=USER_USERDATAS_FILELIST_URL,
    icon="folder",
    perm="filelist.userdatas",
)


class UserDatasFileAddView(FileUploadView):
    _schema = UserDatasFileUploadSchema
    title = "Attacher un fichier au portefeuille de l’entrepreneur"

    def get_schema(self):
        return self._schema()


class UserUserDatasFileAddView(UserDatasFileAddView):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class UserDatasFileEditView(FileEditView):
    _schema = UserDatasFileUploadSchema

    def get_schema(self):
        return self._schema()

    def _get_form_initial_data(self):
        appstruct = super()._get_form_initial_data()
        from caerp.models.career_path import CareerPathFileRel

        q = CareerPathFileRel.query().filter(
            CareerPathFileRel.file_id == appstruct.get("id")
        )
        file_rel = q.first()
        if file_rel is not None:
            appstruct["career_path_id"] = file_rel.career_path_id
        return appstruct


class UserUserDatasFileEditView(UserDatasFileEditView):
    @property
    def current_userdatas(self):
        return self.context.userdatas


class UserDatasFileList(BaseView):
    help_message = "Cette liste présente l’ensemble des documents "
    "déposés dans de MooGLi ainsi que l’ensemble des documents générés "
    "depuis l’onglet Génération de documents. Ces documents sont "
    "visibles par l’entrepreneur."

    @property
    def current_userdatas(self):
        return self.context

    def __call__(self):
        query = files.File.query().options(
            load_only(
                "description",
                "name",
                "updated_at",
                "id",
            )
        )
        query = query.filter_by(parent_id=self.current_userdatas.id).order_by(
            files.File.updated_at.desc()
        )

        return dict(
            title="Portefeuille de documents",
            files=query,
            add_url=self.request.route_path(
                "/userdatas/{id}",
                id=self.current_userdatas.id,
                _query=dict(action="attach_file"),
            ),
            help_message=self.help_message,
        )


class UserUserDatasFileList(UserDatasFileList):
    @property
    def current_userdatas(self):
        return self.context.userdatas


def mydocuments_view(context, request):
    """
    View callable collecting datas for showing the social docs associated to the
    current user's account
    """
    if context.userdatas is not None:
        query = files.File.query()
        documents = (
            query.filter(files.File.parent_id == context.userdatas.id)
            .order_by(files.File.updated_at.desc())
            .all()
        )
    else:
        documents = []
    return dict(
        title="Mes documents",
        documents=documents,
    )


def includeme(config):
    import os

    config.add_route(
        "userdatas_file",
        os.path.join(USERDATAS_ITEM_URL, "file", "{id2}"),
        traverse="/files/{id2}",
    )

    config.add_view(
        UserDatasFileAddView,
        route_name=USERDATAS_ITEM_URL,
        permission="addfile.userdatas",
        request_param="action=attach_file",
        layout="default",
        renderer="caerp:templates/base/formpage.mako",
    )
    config.add_view(
        UserDatasFileEditView,
        route_name="userdatas_file",
        permission="edit.file",
        renderer="caerp:templates/base/formpage.mako",
    )
    config.add_view(
        UserDatasFileList,
        route_name=USERDATAS_FILELIST_URL,
        permission="filelist.userdatas",
        renderer="/userdatas/filelist.mako",
        layout="user",
    )
    config.add_view(
        UserUserDatasFileList,
        route_name=USER_USERDATAS_FILELIST_URL,
        permission="filelist.userdatas",
        renderer="/userdatas/filelist.mako",
        layout="user",
    )
    config.add_view(
        mydocuments_view,
        route_name=USER_USERDATAS_MYDOCUMENTS_URL,
        permission="filelist.userdatas",
        renderer="/mydocuments.mako",
        layout="user",
    )

    def deferred_permission(menu, kw):
        return kw["request"].identity.has_userdatas()

    config.add_company_menu(
        parent="document",
        order=4,
        label="Mes documents",
        route_name=USER_USERDATAS_MYDOCUMENTS_URL,
        route_id_key="user_id",
        permission=deferred_permission,
    )
