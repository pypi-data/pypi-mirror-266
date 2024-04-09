import logging
from deform_extensions import GridFormWidget
import colander
from pyramid.httpexceptions import HTTPFound

from caerp.utils.strings import format_account
from caerp.forms.user.login import (
    get_add_edit_schema,
    get_password_schema,
)
from caerp.views import (
    BaseFormView,
    DisableView,
    DeleteView,
)
from caerp.views.user.routes import (
    USER_ITEM_URL,
    USER_LOGIN_URL,
    USER_LOGIN_ADD_URL,
    USER_LOGIN_EDIT_URL,
    USER_LOGIN_SET_PASSWORD_URL,
    LOGIN_ITEM_URL,
    LOGIN_EDIT_URL,
    LOGIN_SET_PASSWORD_URL,
)
from caerp.views.user.tools import UserFormConfigState

logger = logging.getLogger(__name__)

LOGIN_GRID = (
    (("login", 12),),
    (("pwd_hash", 12),),
    (("primary_group", 12),),
    (("groups", 12),),
    (("estimation_limit_amount", 6), ("invoice_limit_amount", 6)),
    (("supplier_order_limit_amount", 6), ("supplier_invoice_limit_amount", 6)),
)


class LoginAddView(BaseFormView):
    """
    View handling login add
    """

    schema = get_add_edit_schema()

    def __init__(self, *args, **kwargs):
        BaseFormView.__init__(self, *args, **kwargs)
        self.form_config = UserFormConfigState(self.session)

    @property
    def title(self):
        return "Ajouter des identifiants pour le compte {} ({})".format(
            self.context.label, self.context.email
        )

    def before(self, form):
        logger.debug(
            "In the login form, defaults {0}".format(self.form_config.get_defaults())
        )
        form.widget = GridFormWidget(named_grid=LOGIN_GRID)
        form.set_appstruct(
            {
                "login": self.context.email,
                "user_id": self.context.id,
                "primary_group": self.form_config.pop_default(
                    "primary_group", "contractor"
                ),
                "groups": self.form_config.pop_default("groups", []),
            }
        )

    def submit_success(self, appstruct):
        password = appstruct.pop("pwd_hash", None)
        model = self.schema.objectify(appstruct)
        primary_group = appstruct.pop("primary_group", None)
        groups = appstruct.pop("groups", [])
        if groups or primary_group:
            groups = list(groups)
            groups.append(primary_group)
            model.groups = groups

        model.user_id = self.context.id
        model.set_password(password)
        self.dbsession.add(model)
        self.dbsession.flush()

        next_step = self.form_config.get_next_step()
        if next_step is not None:
            redirect = self.request.route_path(
                next_step,
                id=self.context.id,
            )
        else:
            redirect = self.request.route_path(
                USER_ITEM_URL,
                id=self.context.id,
            )
        logger.debug("  + Login  with id {0} added".format(model.id))
        return HTTPFound(redirect)


class LoginEditView(BaseFormView):
    schema = get_add_edit_schema(edit=True)

    def is_my_account_view(self):
        return self.current().user_id == self.request.identity.id

    @property
    def title(self):
        if self.is_my_account_view():
            return "Modification de mes identifiants"
        else:
            return "Modification des identifiants de {0}".format(
                format_account(self.current().user)
            )

    def before(self, form):
        form.widget = GridFormWidget(named_grid=LOGIN_GRID)
        form_fields = {
            "login": self.current().login,
            "primary_group": self.current().primary_group(),
            "groups": self.current().groups,
            "user_id": self.current().user_id,
        }

        if self.current().supplier_order_limit_amount is not None:
            form_fields[
                "supplier_order_limit_amount"
            ] = self.current().supplier_order_limit_amount

        if self.current().supplier_invoice_limit_amount is not None:
            form_fields[
                "supplier_invoice_limit_amount"
            ] = self.current().supplier_invoice_limit_amount

        if self.current().estimation_limit_amount is not None:
            form_fields[
                "estimation_limit_amount"
            ] = self.current().estimation_limit_amount

        if self.current().invoice_limit_amount is not None:
            form_fields["invoice_limit_amount"] = self.current().invoice_limit_amount

        form.set_appstruct(form_fields)

    def current(self):
        return self.context

    def submit_success(self, appstruct):
        password = appstruct.pop("pwd_hash", None)
        model = self.schema.objectify(appstruct, self.current())
        primary_group = appstruct.pop("primary_group", None)
        groups = appstruct.pop("groups", [])
        if groups or primary_group:
            groups = list(groups)
            groups.append(primary_group)
            model.groups = groups
        if password:
            model.set_password(password)

        # Ensure values are positive numbers
        for limit in (
            "supplier_order_limit_amount",
            "supplier_invoice_limit_amount",
            "estimation_limit_amount",
            "invoice_limit_amount",
        ):
            if appstruct.get(limit, None) not in (None, colander.null):
                amount = appstruct.pop(limit)
                setattr(model, limit, abs(amount))

        self.dbsession.merge(model)
        self.dbsession.flush()
        redirect = self.request.route_path(
            USER_LOGIN_URL,
            id=self.current().user_id,
        )
        logger.debug("  + Login  with id {0} modified".format(model.id))
        return HTTPFound(redirect)


class LoginPasswordView(LoginEditView):
    """
    Changer mon mot de passe
    """

    schema = get_password_schema()

    @property
    def title(self):
        if self.is_my_account_view():
            return "Modification de mon mot de passe"
        else:
            return "Modification du mot de passe de {0}".format(
                format_account(self.current().user)
            )


class UserLoginEditView(LoginEditView):
    schema = get_add_edit_schema(edit=True)

    def current(self):
        return self.context.login


class UserLoginPasswordView(UserLoginEditView):
    schema = get_password_schema()

    @property
    def title(self):
        if self.is_my_account_view():
            return "Modification de mon mot de passe"
        else:
            return "Modification du mot de passe de {0}".format(
                format_account(self.current().user)
            )


class LoginDisableView(DisableView):
    def on_disable(self):
        for company in self.context.user.companies:
            active_employees = [
                emp
                for emp in company.employees
                if emp
                and emp.login
                and emp.login.active
                and emp.id != self.context.user.id
            ]
            if company.active and not active_employees:
                company.disable()
                self.request.dbsession.merge(company)

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                USER_LOGIN_URL,
                id=self.context.user_id,
            )
        )


class LoginDeleteView(DeleteView):
    delete_msg = "Les identifiants ont bien été supprimés"

    def redirect(self):
        return HTTPFound(
            self.request.route_path(USER_ITEM_URL, id=self.context.user_id)
        )


def login_view(context, request):
    """
    Return the login view datas
    """
    return dict(login=context.login, title="Identifiants rattachés au compte")


def includeme(config):
    config.add_view(
        login_view,
        route_name=USER_LOGIN_URL,
        permission="view.login",
        renderer="/user/login.mako",
        layout="user",
    )
    config.add_view(
        LoginAddView,
        route_name=USER_LOGIN_URL,
        request_param="action=add",
        permission="add.login",
        renderer="/base/formpage.mako",
        layout="default",
    )
    config.add_view(
        LoginAddView,
        route_name=USER_LOGIN_ADD_URL,
        permission="add.login",
        renderer="/base/formpage.mako",
        layout="default",
    )
    config.add_view(
        UserLoginEditView,
        route_name=USER_LOGIN_EDIT_URL,
        permission="edit.login",
        renderer="/user/edit.mako",
        layout="user",
    )
    config.add_view(
        LoginEditView,
        route_name=LOGIN_EDIT_URL,
        permission="edit.login",
        renderer="/base/formpage.mako",
    )
    config.add_view(
        LoginDisableView,
        route_name=LOGIN_ITEM_URL,
        request_param="action=activate",
        permission="disable.login",
        layout="user",
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        LoginDeleteView,
        route_name=LOGIN_ITEM_URL,
        request_param="action=delete",
        permission="delete.login",
        require_csrf=True,
        request_method="POST",
    )
    config.add_view(
        LoginPasswordView,
        route_name=LOGIN_SET_PASSWORD_URL,
        permission="set_password.login",
        renderer="/base/formpage.mako",
        layout="default",
    )
    config.add_view(
        UserLoginPasswordView,
        route_name=USER_LOGIN_SET_PASSWORD_URL,
        permission="set_password.login",
        renderer="/user/edit.mako",
        layout="user",
    )
