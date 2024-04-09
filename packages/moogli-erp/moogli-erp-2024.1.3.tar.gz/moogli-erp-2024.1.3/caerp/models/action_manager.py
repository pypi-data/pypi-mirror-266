import datetime
import logging
from caerp.exception import (
    Forbidden,
    BadRequest,
)


logger = logging.getLogger(__name__)


class Action:
    """
    a state object with a name, permission and a callback callbacktion
    :param name: The state name
    :param permission: The permission needed to set this state
    :param callback: A callback function to call on state process
    :param status_attr: The attribute storing the model's status
    :param userid_attr: The attribute storing the status person's id
    :param prev_status: the allowed previous status (None to allow all)
    """

    def __init__(
        self,
        name,
        permission,
        prev_status=None,
        callback=None,
        status_attr=None,
        userid_attr=None,
        datetime_attr=None,
        **kwargs,
    ):
        self.name = name
        self.prev_status = prev_status
        if not isinstance(permission, (list, tuple)):
            permission = [permission]
        self.permissions = permission
        self.set_callbacks(callback)
        self.status_attr = status_attr
        self.userid_attr = userid_attr
        self.datetime_attr = datetime_attr
        self.options = kwargs

    def set_callbacks(self, callback):
        if callback and not isinstance(callback, (list, tuple)):
            callback = [callback]
        self.callbacks = callback

    def _transition_allowed(self, context):
        """
        Checks if the status is allowed regarding the current status and
        prev_status requirement.

        """
        return self.prev_status is None or self.prev_status == getattr(
            context, self.status_attr
        )

    def allowed(self, request, context):
        """
        return True if this state assignement on context is allowed
        in the current request

        :param obj context: An object with acl
        :param obj request: The Pyramid request object
        :returns: True/False
        :rtype: bool
        """
        if len(self.permissions) == 0:
            user_allowed = True
        else:
            user_allowed = False
            for permission in self.permissions:
                if request.has_permission(permission, context):
                    user_allowed = True
                    break

        transition_allowed = self._transition_allowed(context)

        return user_allowed and transition_allowed

    def __json__(self, request):
        result = dict(
            status=self.name,
            value=self.name,
        )
        result.update(self.options)
        return result

    def process(self, request, model, user_id, **kw):
        """
        Process the action

        Set the model's status_attr if needed (status)
        Set the model's status user_id attribute if needed (status_user_id)

        Fire a callback if needed
        """
        if self.status_attr is not None:
            setattr(model, self.status_attr, self.name)
        if self.userid_attr:
            setattr(model, self.userid_attr, user_id)
        if self.datetime_attr:
            setattr(model, self.datetime_attr, datetime.datetime.now())

        if self.callbacks:
            for callback in self.callbacks:
                model = callback(request, model, user_id=user_id, **kw)

        return model

    def __repr__(self):
        return "< State %s allowed for %s (status_attr : %s, " "userid_attr : %s )>" % (
            self.name,
            self.permissions,
            self.status_attr,
            self.userid_attr,
        )


class ActionManager:
    def __init__(self):
        self.items = []

    def add(self, action):
        self.items.append(action)

    def get_allowed_actions(self, request, context=None):
        """
        Return the list of next available actions regarding the current user
        perm's
        """
        result = []
        context = context or request.context

        for action in self.items:
            if action.allowed(request, context):
                result.append(action)
        return result

    def _get_action(self, context, action_name):
        """
        Retrieve the action called "action_name"

        :param context: context object
        :param str action_name: The name of the action we're looking for
        :returns: An instance of Action
        """
        action = None
        for item in self.items:
            if item.name == action_name:
                if item.prev_status is None:
                    action = item
                else:
                    current_status = getattr(context, item.status_attr)
                    if item.prev_status == current_status:
                        action = item
            if action is not None:
                break  # First match wins
        return action

    def check_allowed(self, request, context, action_name):
        """
        Check that the given status could be set on the current context

        :param obj request: The current request object
        :param obj context: The context to manage
        :param str action_name: The name of the action
        :raises: Forbidden if the action isn't allowed
        :raises: BadRequest if the action doesn't exists
        """
        context = context or request.context
        action = self._get_action(context, action_name)

        if action is None:
            logger.error("Unknown action : %s" % action_name)
            raise BadRequest()

        elif not action.allowed(request, context):
            raise Forbidden(
                "This action {} is not allowed for user with id {} (needed permissions {})".format(
                    action_name,
                    request.identity.id,
                    action.permissions,
                )
            )
        return action

    def process(self, request, context, action_name, **params):
        """
        Process a specific action

        :param str action_name: The name of the action
        :param obj context: The context to manage
        :param obj request: The current request object
        :param dict params: The params to pass to the callback

        :raises: colander.Invalid if the action is unknown
        :raises: Forbidden if the action is not allowed for the current request
        """
        action = self.check_allowed(request, context, action_name)
        return action.process(request, context, request.identity.id, **params)


def get_validation_state_manager(
    data_type: str,
    userid_attr: str = "status_user_id",
    datetime_attr: str = "status_date",
    callbacks: dict = {},
) -> ActionManager:
    """
    Return a state machine handling the basic states

    :param datetime_attr: the attribute storing the last status change
    :param data_type: estimation/invoice/cancelinvoice/expensesheet
    :param userid_attr: the attribute holding the user who changed status

    :returns: An action manager machine that can be used to perform state
    changes
    """
    manager = ActionManager()
    for status, prev_status, icon, label, title, css in (
        (
            "valid",
            None,
            "check-circle",
            "Valider",
            "Valider ce document (il ne pourra plus être modifié)",
            "btn-primary icon_only_mobile icon_only_tablet",
        ),
        (
            "wait",
            None,
            "clock",
            "Demander la validation",
            "Enregistrer ce document et en demander la validation",
            "btn-primary icon_only_mobile icon_only_tablet",
        ),
        (
            "invalid",
            None,
            "times-circle",
            "Invalider",
            "Invalider ce document afin que l’entrepreneur le corrige",
            "btn-primary negative icon_only_mobile icon_only_tablet",
        ),
        (
            "draft",
            "wait",
            "pen",
            "Repasser en brouillon",
            "Repasser ce document en brouillon pour pouvoir le modifier",
            "icon_only_mobile icon_only_tablet",
        ),
    ):
        action = Action(
            status,
            "%s.%s" % (status, data_type),
            prev_status=prev_status,
            status_attr="status",
            userid_attr=userid_attr,
            datetime_attr=datetime_attr,
            icon=icon,
            label=label,
            title=title,
            css=css,
        )
        if status in callbacks:
            action.set_callbacks(callbacks[status])
        manager.add(action)
    return manager
