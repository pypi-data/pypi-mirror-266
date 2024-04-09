import logging
import colander
from caerp_celery.models import FileGenerationJob

from sqlalchemy import (
    or_,
    distinct,
)

from caerp_celery.tasks.export import export_to_file

from caerp.models.user.userdatas import (
    UserDatas,
    CompanyDatas,
)
from caerp.forms.user.userdatas import get_list_schema
from caerp.utils.widgets import (
    Link,
    POSTButton,
)
from caerp.views import AsyncJobMixin, BaseListView
from caerp.views.userdatas.routes import (
    USERDATAS_URL,
    USERDATAS_XLS_URL,
    USERDATAS_CSV_URL,
    USERDATAS_ODS_URL,
    USER_USERDATAS_EDIT_URL,
    USERDATAS_ITEM_URL,
)


logger = logging.getLogger(__name__)


class UserDatasListClass:
    """
    User datas list view
    """

    title = "Liste des informations sociales"
    schema = get_list_schema()
    sort_columns = dict(
        lastname=UserDatas.coordonnees_lastname,
    )
    default_sort = "lastname"

    def query(self):
        return UserDatas.query()

    def filter_situation_situation(self, query, appstruct):
        """
        Filter the general situation of the project
        """
        logger.debug("APPSTRUCT : %s" % appstruct)
        situation = appstruct.get("situation_situation")
        if situation not in (None, "", colander.null):
            query = query.filter(UserDatas.situation_situation_id == situation)
        return query

    def filter_search(self, query, appstruct):
        """
        Filter the current query for firstname, lastname or activity
        """
        search = appstruct.get("search")

        if search not in (None, "", colander.null):
            filter_ = "%" + search + "%"
            query = query.filter(
                or_(
                    UserDatas.coordonnees_firstname.like(filter_),
                    UserDatas.coordonnees_lastname.like(filter_),
                    UserDatas.activity_companydatas.any(
                        CompanyDatas.name.like(filter_)
                    ),
                    UserDatas.activity_companydatas.any(
                        CompanyDatas.title.like(filter_)
                    ),
                )
            )
        return query

    def filter_situation_follower_id(self, query, appstruct):
        """
        Filter the current query through followers
        """
        follower_id = appstruct.get("situation_follower_id")

        if follower_id not in (None, -1, colander.null):
            query = query.filter(UserDatas.situation_follower_id == follower_id)
        return query

    def filter_situation_antenne_id(self, query, appstruct):
        """
        Filter the current query with antenne id
        """
        antenne_id = appstruct.get("situation_antenne_id")

        if antenne_id not in (None, -1, colander.null):
            query = query.filter(UserDatas.situation_antenne_id == antenne_id)
        return query


class UserDatasListView(UserDatasListClass, BaseListView):
    """
    The userdatas listing view
    """

    add_template_vars = ("stream_actions",)

    def stream_actions(self, item):
        """
        Stream actions available for the given item
        """
        yield Link(
            self.request.route_path(USER_USERDATAS_EDIT_URL, id=item.user_id),
            "Voir",
            title="Voir / Modifier les données de gestion sociales",
            icon="pen",
            css="icon",
        )

        yield POSTButton(
            self.request.route_path(
                USERDATAS_ITEM_URL, id=item.id, _query={"action": "delete"}
            ),
            "Supprimer",
            title="Supprimer la fiche de gestion sociale",
            icon="trash-alt",
            css="icon negative",
            confirm="En supprimant cette fiche de "
            "gestion sociale, vous supprimerez également \n"
            "les données associées (documents sociaux, "
            "parcours, historiques…). \n\nContinuer ?",
        )


class UserDatasXlsView(
    AsyncJobMixin,
    UserDatasListClass,
    BaseListView,
):
    """Userdatas excel view"""

    model = UserDatas
    file_format = "xls"
    filename = "gestion_sociale_"

    def query(self):
        return self.request.dbsession.query(distinct(UserDatas.id))

    def _build_return_value(self, schema, appstruct, query):
        """
        Return the streamed file object
        """
        all_ids = [elem[0] for elem in query]

        if not all_ids:
            msg = "Il n'y a aucun élément à exporter"
            return self.show_error(msg)

        celery_error_resp = self.is_celery_alive()
        if celery_error_resp:
            return celery_error_resp

        job_result = self.initialize_job_result(FileGenerationJob)
        celery_job = export_to_file.delay(
            job_result.id, "userdatas", all_ids, self.filename, self.file_format
        )
        return self.redirect_to_job_watch(celery_job, job_result)


class UserDatasOdsView(UserDatasXlsView):
    file_format = "ods"


class UserDatasCsvView(UserDatasXlsView):
    file_format = "csv"


def includeme(config):
    """
    Add module related views
    """
    config.add_view(
        UserDatasListView,
        route_name=USERDATAS_URL,
        renderer="/userdatas/list.mako",
        permission="admin_userdatas",
    )

    config.add_view(
        UserDatasXlsView,
        route_name=USERDATAS_XLS_URL,
        permission="admin_userdatas",
    )

    config.add_view(
        UserDatasOdsView,
        route_name=USERDATAS_ODS_URL,
        permission="admin_userdatas",
    )

    config.add_view(
        UserDatasCsvView,
        route_name=USERDATAS_CSV_URL,
        permission="admin_userdatas",
    )
    config.add_admin_menu(
        parent="userdata", order=0, label="Consulter", href="/userdatas"
    )
