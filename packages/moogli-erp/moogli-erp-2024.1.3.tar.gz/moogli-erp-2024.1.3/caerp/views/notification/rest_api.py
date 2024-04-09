import datetime
from .routes import ITEM_ROUTE, COLLECTION_ROUTE, ACTION_ROUTE

from caerp.models.notification import Notification
from caerp.forms.notification import get_list_schema
from caerp.views import BaseRestView, RestListMixinClass


class NotificationRestApiView(BaseRestView, RestListMixinClass):
    sort_columns = {"due_date": "due_date", "key": "key"}
    default_sort = "due_date"
    default_direction = "desc"
    list_schema = staticmethod(get_list_schema)

    def query(self):
        return (
            Notification.query()
            .filter(Notification.user_id == self.request.identity.id)
            .filter(Notification.read == False)
        )

    def filter_due_date(self, query, appstruct):
        due_date = appstruct.get("filter_due_date", datetime.datetime.now())
        return query.filter(Notification.due_date <= due_date)

    def filter_key(self, query, appstruct):
        key = appstruct.get("filter_key")
        if key:
            query = query.filter(Notification.key == key)
        return query

    def filter_channel(self, query, appstruct):
        channel = appstruct.get("filter_channel")
        if channel:
            query = query.filter(Notification.channel == channel)
        return query

    def mark_read_endpoint(self):
        """Api endpoint that mark a notification as read"""
        self.context.read = True
        self.dbsession.merge(self.context)
        self.dbsession.flush()
        return self.get()

    def postpone_endpoint(self):
        """Api endpoint that postpone a notification in time"""
        self.context.postpone(self.request)
        self.dbsession.merge(self.context)
        self.dbsession.flush()
        return self.get()


def includeme(config):
    config.add_rest_service(
        NotificationRestApiView,
        route_name=ITEM_ROUTE,
        collection_route_name=COLLECTION_ROUTE,
        view_rights="view.notification",
        edit_rights="edit.notification",
        delete_rights="delete.notification",
        collection_view_rights="view",
    )
    config.add_view(
        NotificationRestApiView,
        route_name=ACTION_ROUTE,
        attr="mark_read_endpoint",
        match_param="action_name=mark_read",
        request_method=("PUT", "POST"),
        permission="edit.notification",
        renderer="json",
    )
    config.add_view(
        NotificationRestApiView,
        route_name=ACTION_ROUTE,
        attr="postpone_endpoint",
        match_param="action_name=postpone",
        request_method=("PUT", "POST"),
        permission="edit.notification",
        renderer="json",
    )
