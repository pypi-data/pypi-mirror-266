# -*- coding:utf-8 -*-

import colander
import deform
from sqlalchemy import or_
from sqlalchemy.orm import load_only

from caerp_base.models.base import DBSESSION
from caerp import forms
from caerp.utils.strings import (
    format_account,
)

from caerp.models.user.user import User
from caerp.models.user.userdatas import AntenneOption
from caerp.models.user.login import Login
from caerp.models.user.group import Group


def _filter_by_group(query, groups):
    """
    Collect users belonging to a given group

    :param list groups: List of groups as strings
    :returns: User belonging to this group
    """
    if groups:
        if len(groups) > 1:
            clauses = []
            for group in groups:
                clauses.append(Login.groups.any(Group.name == group))

            return query.filter(or_(*clauses))
        else:
            return query.filter(Login.groups.any(Group.name == groups[0]))
    return query


def get_users_options(roles=None):
    """
    Return the list of active users from the database formatted as choices:
        [(user_id, user_label)...]

    :param role: roles of the users we want
        default:  all
        values : ('contractor', 'manager', 'admin'))
    """
    query = DBSESSION().query(User).options(load_only("id", "firstname", "lastname"))

    # Only User accounts with logins
    query = query.join(Login).filter(Login.active == True)

    query = query.filter(User.id > 0)
    query = query.order_by(User.lastname)

    if roles and not hasattr(roles, "__iter__"):
        roles = [roles]

    query = _filter_by_group(query, roles)
    return [(str(u.id), format_account(u)) for u in query]


def get_deferred_user_choice(roles=None, widget_options=None):
    """
    Return a colander deferred for users selection options
    """
    widget_options = widget_options or {}
    default_option = widget_options.pop("default_option", None)

    @colander.deferred
    def user_select(node, kw):
        """
        Return a user select widget
        """
        choices = get_users_options(roles)
        if default_option:
            # Use of placeholder arg is mandatory with Select2 ; otherwise, the
            # clear button crashes. https://github.com/select2/select2/issues/5725
            # Cleaner fix would be to replace `default_option` 2-uple arg with
            # a `placeholder` str arg, as in JS code.
            choices.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]
        return deform.widget.Select2Widget(values=choices, **widget_options)

    return user_select


def get_deferred_follower_choice(widget_options=None, no_follower=False):
    """
    Return a colander deferred for users selection options
    """
    widget_options = widget_options or {}
    default_option = widget_options.pop("default_option", None)

    @colander.deferred
    def follower_select(node, kw):
        """
        Return a user select widget
        """
        choices = get_users_options(["admin", "manager"])
        optgroup = deform.widget.OptGroup("Accompagnateurs", *choices)

        choices = []
        choices.append(optgroup)

        if no_follower:
            choices.insert(0, (-2, "Sans accompagnateur paramétré"))

        if default_option:
            choices.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]

        return deform.widget.Select2Widget(values=choices, **widget_options)

    return follower_select


def get_antenne_options(roles=None):
    """
    Return the list of active users from the database formatted as choices:
        [(user_id, user_label)...]

    :param role: roles of the users we want
        default:  all
        values : ('contractor', 'manager', 'admin'))
    """
    query = DBSESSION().query(AntenneOption).options(load_only("id", "label"))
    query = query.order_by(AntenneOption.order)

    antennes_choice = [(str(a.id), a.label) for a in query]

    return antennes_choice


def get_deferred_antenne_choice(multi_companies=True, widget_options=None):
    """
    Return a colander deferred for antenne selection options
    """
    widget_options = widget_options or {}
    default_option = widget_options.pop("default_option", None)

    @colander.deferred
    def antenne_select(node, kw):
        """
        Return a antenne select widget
        """
        antenne_options = get_antenne_options()
        optgroup = deform.widget.OptGroup("Antennes", *antenne_options)

        choices = []
        choices.append(optgroup)

        if multi_companies:
            choices.insert(0, (-1, "Enseignes multi ES"))
            choices.insert(1, (-2, "Sans antennes paramétrées"))
        else:
            choices.insert(0, (-2, "Sans antennes paramétrées"))

        if default_option:
            choices.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]

        return deform.widget.Select2Widget(values=choices, **widget_options)

    return antenne_select


def user_node(roles=None, multiple=False, **kw):
    """
    Return a schema node for user selection
    roles: allow to restrict the selection to the given roles
        (to select between admin, contractor and manager)
    """
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=get_deferred_user_choice(roles, widget_options),
        **kw,
    )


def antenne_node(multi_companies=True, multiple=False, **kw):
    """
    Return a schema node for antenne selection
    """
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=get_deferred_antenne_choice(multi_companies, widget_options),
        **kw,
    )


def follower_node(multiple=False, **kw):
    """
    Return a schema node for follower selection
    """
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Set() if multiple else colander.Integer(),
        widget=get_deferred_follower_choice(
            widget_options=widget_options,
            no_follower=True,
        ),
        **kw,
    )


contractor_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    empty_filter_msg="Tous",
    title="Entrepreneur",
)

validator_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    empty_filter_msg="Tous",
    title="Validé par",
    roles=["manager", "admin"],
)

issuer_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    empty_filter_msg="Tous",
    title="Enregistré par",
    roles=["manager", "admin"],
)

antenne_filter_node_factory = forms.mk_filter_node_factory(
    antenne_node,
    empty_filter_msg="Toutes",
    title="Antenne de rattachement de l'enseigne",
    multi_companies=False,
)

follower_filter_node_factory = forms.mk_filter_node_factory(
    follower_node,
    empty_filter_msg="Tous",
    title="Accompagnateur de l'enseigne",
)

conseiller_choice_node = forms.mk_choice_node_factory(
    user_node,
    resource_name="un accompagnateur",
    roles=["manager", "admin"],
)

conseiller_filter_node_factory = forms.mk_filter_node_factory(
    user_node,
    empty_filter_msg="Tous",
    title="Accompagnateur",
    roles=["manager", "admin"],
)

contractor_choice_node_factory = forms.mk_choice_node_factory(
    user_node,
    resource_name="un entrepreneur",
    roles=["contractor"],
)


@colander.deferred
def deferred_user_groups_datas_select(node, kw):
    values = Group.query("id", "label").all()
    values.insert(0, ("", "- Sélectionner un rôle"))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def deferred_user_groups_datas_validator(node, kw):
    ids = [entry[0] for entry in Group.query("id")]
    return colander.OneOf(ids)
