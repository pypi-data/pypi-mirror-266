"""
    Form schemas for project edition
"""
import colander

import logging
import deform
import functools
from sqlalchemy import select
from colanderalchemy import SQLAlchemySchemaNode

from caerp.models.task import Task
from caerp.models.third_party.customer import Customer
from caerp.models.project import (
    Project,
)
from caerp.models.project.types import (
    ProjectType,
    BusinessType,
)
from caerp import forms
from caerp.forms.lists import BaseListsSchema

logger = logging.getLogger(__name__)


COMPUTE_MODES = [
    ("ht", "Mode HT (par défaut)"),
    ("ttc", "Mode TTC"),
]


def get_compute_modes(request, project: Project = None) -> list:
    """Return the list of available compute modes

    :param project: _description_, defaults to None

    :return: list of available compute mode options
    """
    # TODO : permettre de désactive le mode de calcul HT dans l'admin de MooGLi
    # et implémenter le traitement ici
    result = []
    if (
        ProjectType.query()
        .filter(ProjectType.ht_compute_mode_allowed == True, ProjectType.active == True)
        .count()
        > 0
    ):
        result.append(("ht", "Mode HT (par défaut)"))
    if (
        ProjectType.query()
        .filter(
            ProjectType.ttc_compute_mode_allowed == True, ProjectType.active == True
        )
        .count()
        > 0
    ):
        result.append(("ttc", "Mode TTC"))
    return result


def customer_objectify(id_):
    """
    Objectify the associated form node schema (an id schemanode)

    Return the customer object with the given id_

    Note :
        colanderalchemy schemanode is to a model and provides a objectify
        methodused to convert an appstruct to the appropriate model. For the
        project->customer relationship, we need to be able to configure only
        existing elements. Since we didn't found a clear way to do it with
        colanderalchemy, we add the node manually and fit the colanderalchemy
        way of working by implementing usefull methods (namely objectify and
        dictify)
    """
    obj = Customer.get(id_)
    return obj


def customer_dictify(obj):
    """
    Return a representation of the current model, used to fill the associated
    form node
    """
    return obj.id


def check_begin_end_date(form, value):
    """
    Check the project beginning date preceeds the end date
    """
    ending = value.get("ending_date")
    starting = value.get("starting_date")

    if ending is not None and starting is not None:
        if not ending >= starting:
            exc = colander.Invalid(
                form, "La date de début doit précéder la date de fin du dossier"
            )
            exc["starting_date"] = "Doit précéder la date de fin"
            raise exc


@colander.deferred
def deferred_default_project_type(node, kw):
    """
    Load the default ProjectType on bind
    """
    query = select(ProjectType.id).where(ProjectType.default == True)
    data = kw["request"].dbsession.execute(query).scalar()

    if data is None:
        data = colander.null
    return data


def _is_compatible_project_type(project, project_type):
    """
    Check the given project type is compatible with the current project

    If the project contains a document which is of associated to a business
    type that is not provided by the given project_type, we can't move the
    project to this new type
    """
    project_btype_ids = project.get_used_business_type_ids()
    project_type_btype_ids = project_type.get_business_type_ids()
    return set(project_btype_ids).issubset(set(project_type_btype_ids))


def get_project_type_options(request):
    """
    collect project type options
    """
    project_types = ProjectType.query_for_select()

    context = request.context
    if isinstance(context, Project):
        company = context.company
    else:
        company = context

    for project_type in project_types:
        # Prevent project_type without default business_type bug
        if project_type.default_business_type is None:
            continue

        if (
            not project_type.private
            or project_type.default
            or request.has_permission("add.%s" % project_type.name, company)
        ):
            if isinstance(context, Project):
                if not _is_compatible_project_type(context, project_type):
                    continue
            yield project_type


@colander.deferred
def deferred_project_type_widget(node, kw):
    """
    Build a ProjectType radio checkbox widget on bind
    Filter project types by active and folowing the associated rights
    """
    request = kw["request"]
    values = [
        (project_type.id, project_type.label)
        for project_type in get_project_type_options(request)
    ]

    if len(values) <= 1:
        return deform.widget.HiddenWidget()
    else:
        return deform.widget.RadioChoiceWidget(values=values)


@colander.deferred
def deferred_project_type_validator(node, kw):
    request = kw["request"]
    return colander.OneOf([ptype.id for ptype in get_project_type_options(request)])


@colander.deferred
def deferred_readonly_project_type_widget(node, kw):
    """
    Build a readonly ProjectType radio checkbox widget on bind
    Filter project types by active and folowing the associated rights
    """
    request = kw["request"]
    values = [
        (project_type.id, project_type.label)
        for project_type in get_project_type_options(request)
    ]

    if len(values) <= 1:
        return deform.widget.HiddenWidget()
    else:
        return deform.widget.RadioChoiceWidget(values=values, readonly=True)


def get_business_type_options(request):
    """
    collect business types accessible for the current user
    """
    business_types_query = BusinessType.query_for_select()
    if isinstance(request.context, Project):
        ptype_id = request.context.project_type_id
        business_types_query = business_types_query.filter(
            BusinessType.other_project_types.any(ProjectType.id == ptype_id)
        )

    values = []
    for business_type in business_types_query:
        if not business_type.private or request.has_permission(
            "add.%s" % business_type.name
        ):
            values.append(business_type)
    return values


@colander.deferred
def deferred_business_type_widget(node, kw):
    """
    Build a BusinessType checkbox list widget on bind

    Only show active businesstypes than can be associated to the current's
    project type
    """
    request = kw["request"]
    business_types = get_business_type_options(request)
    values = []
    for business_type in business_types:
        values.append((business_type.id, business_type.label))
    return deform.widget.CheckboxChoiceWidget(values=values)


@colander.deferred
def deferred_business_type_title(node, kw):
    request = kw["request"]
    business_types = get_business_type_options(request)
    count = len(business_types)
    if count == 0:
        description = ""
    else:
        description = "Type(s) d'affaire qui peut être mené dans ce dossier "

        if isinstance(request.context, Project):
            default = request.context.project_type.default_business_type

            if default is not None:
                description = "%s (autre que le type par défaut : %s)" % (
                    description,
                    default.label,
                )
    return description


@colander.deferred
def deferred_mode_widget(node, kw):
    compute_modes = get_compute_modes(kw["request"])
    if isinstance(kw["request"].context, Project):
        project: Project = kw["request"].context
        if len(compute_modes) > 1 and not project.has_internal_customer():
            widget = deform.widget.RadioChoiceWidget(values=compute_modes)
        else:
            widget = deform.widget.HiddenWidget()
    else:
        widget = deform.widget.RadioChoiceWidget(values=compute_modes)
    return widget


def _customize_project_schema(schema):
    """
    Customize the project schema to add widgets/validators ...

    :param obj schema: a colander.SchemaNode instance
    """
    customize = functools.partial(forms.customize_field, schema)
    if "name" in schema:
        customize("name", missing=colander.required, title="Nom du dossier")

    if "project_type_id" in schema:
        customize(
            "project_type_id",
            widget=deferred_project_type_widget,
            default=deferred_default_project_type,
            validator=deferred_project_type_validator,
            missing=colander.required,
        )

    if "starting_date" in schema:
        schema.validator = check_begin_end_date

    if "business_types" in schema:
        customize(
            "business_types",
            title=deferred_business_type_title,
            missing=colander.drop,
            children=[forms.get_sequence_child_item_id_node(BusinessType)],
            widget=deferred_business_type_widget,
        )

    if "mode" in schema:
        customize(
            "mode",
            title="Mode de saisie des prix de vente",
            description="""
            Les modes de saisie définissent l'approche et la construction de
            vos devis et factures. Ils modifient les formules de calcul ainsi
            que la présentation du document pour vous et pour votre client.
            """,
            widget=deferred_mode_widget,
            default="ht",
        )
    return schema


def project_add_data_integrity(form, appstruct):
    """Check that the submitted data are compatible with each others"""
    project_type_id = appstruct["project_type_id"]
    ptype = ProjectType.get(project_type_id)
    business_type_ids = appstruct.get("business_types")
    for business_type_id in business_type_ids:
        btype = BusinessType.get(business_type_id)
        if ptype not in btype.other_project_types:
            raise colander.Invalid(
                form,
                "Le type d'affaire {} n'est pas compatible avec le type de "
                "projet {}".format(btype.name, ptype.name),
            )
    mode = appstruct.get("mode")

    if mode == "ht" and not ptype.ht_compute_mode_allowed:
        raise colander.Invalid(
            form, "Le mode HT n'est pas autorisé dans ce type de projet"
        )
    elif mode == "ttc" and not ptype.ttc_compute_mode_allowed:
        raise colander.Invalid(
            form, "Le mode TTC n'est pas autorisé dans ce type de projet"
        )


def get_full_add_project_schema() -> SQLAlchemySchemaNode:
    """
    Build an add project schema with all creation fields
    Used in the REST Api for adding project from js based UIs
    """
    schema = SQLAlchemySchemaNode(
        Project,
        includes=(
            "name",
            "project_type_id",
            "code",
            "description",
            "definition",
            "starting_date",
            "ending_date",
            "business_types",
            "mode",
        ),
    )
    _customize_project_schema(schema)
    schema.validator = project_add_data_integrity
    return schema


@colander.deferred
def deferred_keep_customers_preparer(node, kw):
    """
    Ensure that all customer for which we have an estimation/invoice
    are still attached to the project (add them to the submitted values)
    """
    request = kw["request"]
    project = request.context
    if not isinstance(project, Project):
        return forms.uniq_entries_preparer

    project_customer_ids = [
        entry[0]
        for entry in request.dbsession.query(Task.customer_id).filter(
            Task.project_id == project.id
        )
    ]

    def _ensure_customer_in_list(submitted):
        customer_ids = project_customer_ids
        if submitted:
            customer_ids.extend(submitted)
        customer_ids = forms.uniq_entries_preparer(customer_ids)
        return customer_ids

    return _ensure_customer_in_list


#
# Ref #3599 : Le validateur renvoyé par customer_choice_node_factory ne contient que
# les ids des clients actifs
# Quand on modifie un projet, on veut aussi maintenir les clients archivés dans le
# projet, on utilise donc un validateur custom
#
@colander.deferred
def deferred_project_customer_id_validator(node, kw):
    request = kw["request"]
    project = request.context
    ids = request.dbsession.query(Customer.id).filter(
        Customer.company_id == project.company_id
    )
    if project.mode == "ttc":
        ids = ids.filter(Customer.type != "internal")
    return colander.OneOf([i[0] for i in ids])


def _add_customer_node_to_schema(schema, edit=False):
    """
    Build a custom customer selection node and add it to the schema

    :param obj schema: a colander.SchemaNode instance
    """
    # Add a custom node to be able to associate existing customers
    from caerp.forms.third_party.customer import customer_choice_node_factory

    customer_id_node = customer_choice_node_factory(
        name="customer_id", title="un client", missing=colander.drop
    )

    if edit:
        # On veut un autre validateur uniquement quand on édite un projet
        customer_id_node.validator = deferred_project_customer_id_validator

    customer_id_node.objectify = customer_objectify
    customer_id_node.dictify = customer_dictify

    schema.add(
        colander.SchemaNode(
            colander.Sequence(),
            customer_id_node,
            widget=deform.widget.SequenceWidget(min_len=1),
            title="Clients",
            name="customers",
            preparer=deferred_keep_customers_preparer,
        )
    )
    return schema


def get_add_project_schema():
    """
    Build a schema for project add
    """
    schema = SQLAlchemySchemaNode(Project, includes=("name", "project_type_id"))
    _customize_project_schema(schema)
    _add_customer_node_to_schema(schema, edit=False)
    return schema


def _alter_step2_form_after_bind(schema, kw):
    """
    Change the step2 form after binding the schema
    """
    if "mode" in schema:
        pt = kw["request"].context.project_type

        # No choice to be made
        if not (pt.ht_compute_mode_allowed and pt.ttc_compute_mode_allowed):
            del schema["mode"]


def get_add_step2_project_schema():
    """
    Build a schema for the second step of project add
    """
    schema = SQLAlchemySchemaNode(
        Project,
        includes=(
            "code",
            "description",
            "definition",
            "starting_date",
            "ending_date",
            "business_types",
            "mode",
        ),
    )
    _customize_project_schema(schema)
    schema.after_bind = _alter_step2_form_after_bind
    return schema


def get_edit_project_schema():
    """
    Return the project Edition/add form schema
    """
    excludes = (
        "_acl",
        "id",
        "company_id",
        "archived",
        "customers",
        "invoices",
        "tasks",
        "estimations",
        "cancelinvoices",
        "project_type",
        "business_types",
        "project_type_id",
        "mode",
    )
    schema = SQLAlchemySchemaNode(Project, excludes=excludes)
    _customize_project_schema(schema)
    _add_customer_node_to_schema(schema, edit=True)
    return schema


class PhaseSchema(colander.MappingSchema):
    """
    Schema for phase
    """

    name = colander.SchemaNode(
        colander.String(),
        title="Nom du sous-dossier",
        validator=colander.Length(max=150),
    )


# Schéma pour les vues liste


@colander.deferred
def deferred_project_type_select_widget(node, kw):
    """
    Load the appropriate widget for project type selection
    """
    request = kw["request"]
    values = [
        (project_type.id, project_type.label)
        for project_type in get_project_type_options(request)
    ]

    if len(values) <= 1:
        return deform.widget.HiddenWidget()
    else:
        values.insert(0, ("", "Tous"))
        return deform.widget.SelectWidget(values=values)


class ProjectListSchema(BaseListsSchema):
    project_type_id = colander.SchemaNode(
        colander.Integer(),
        title="Type de dossier",
        widget=deferred_project_type_select_widget,
        missing=colander.drop,
        insert_before="items_per_page",
    )
    archived = colander.SchemaNode(
        colander.Boolean(),
        title="Inclure les dossiers archivés",
        missing=False,
        insert_before="items_per_page",
    )


class APIProjectListSchema(BaseListsSchema):
    archived = colander.SchemaNode(
        colander.Boolean(),
        missing=False,
    )
    customer_id = colander.SchemaNode(
        colander.Integer(),
        missing=colander.drop,
    )


class APIBusinessListSchema(BaseListsSchema):
    project_type_id = colander.SchemaNode(
        colander.Integer(), missing=None, validator=deferred_project_type_validator
    )


def get_list_schema():
    """
    Return the schema for the project search form
    :rtype: colander.Schema
    """
    schema = ProjectListSchema()
    schema["search"].title = "Dossier ou nom du client"
    return schema


# Outils pour construire un sélecteur de Project


def get_projects_from_request(request):
    """
    Extract a projects list from the request object

    :param obj request: The pyramid request object
    :returns: A list of projects
    :rtype: list
    """
    company_id = request.context.company.id

    projects = Project.label_query()
    projects = projects.filter_by(company_id=company_id)
    projects = projects.filter_by(archived=False)

    if isinstance(request.context, Customer) and request.context.is_internal():
        projects = projects.filter_by(mode="ht")

    return projects.order_by(Project.name)


def _build_project_select_value(project):
    """
    return the tuple for building project select
    """
    label = project.name
    if project.code:
        label += " ({0})".format(project.code)
    return project.id, label


def build_project_values(projects):
    """
    Build human understandable customer labels
    allowing efficient discrimination
    """
    return [_build_project_select_value(project) for project in projects]


def get_deferred_project_select(
    query_func=get_projects_from_request, default_option=None, **widget_options
):
    """
    Dynamically build a deferred project select with (or without) a void
    default value

    """

    @colander.deferred
    def deferred_project_select(node, kw):
        """
        Collecting project select datas from the given request's context

        :param dict kw: Binding dict containing a request key
        :returns: A deform.widget.Select2Widget
        """
        request = kw["request"]
        projects = query_func(request)
        values = list(build_project_values(projects))
        if default_option is not None:
            # Cleaner fix would be to replace `default_option` 2-uple arg with
            # a `placeholder` str arg, as in JS code.
            # Use of placeholder arg is mandatory with Select2 ; otherwise, the
            # clear button crashes. https://github.com/select2/select2/issues/5725
            values.insert(0, default_option)
            widget_options["placeholder"] = default_option[1]

        return deform.widget.Select2Widget(values=values, **widget_options)

    return deferred_project_select


def get_deferred_project_select_validator(query_func=get_projects_from_request):
    @colander.deferred
    def deferred_project_validator(node, kw):
        """
        Build a project option validator based on the request's context

        :param dict kw: Binding dict containing a request key
        :returns: A colander validator
        """
        request = kw["request"]
        projects = query_func(request)
        project_ids = [project.id for project in projects]

        def project_oneof(value):
            if value in ("0", 0):
                return "Veuillez choisir un dossier"
            elif value not in project_ids:
                return "Entrée invalide"
            return True

        return colander.Function(project_oneof)


def project_node_factory(**kw):
    """
    Shortcut used to build a colander schema node

    all arguments are optionnal

    Allow following options :

        any key under kw

            colander.SchemaNode options :

                * title,
                * description,
                * default,
                * missing
                * ...

        widget_options

            deform.widget.Select2Widget options as a dict

        query_func

            A callable expecting the request parameter and returning the
            current customer that should be selected

    e.g:

        >>> get_projects_from_request(
            title="Project",
            query_func=get_projects_list,
            default=get_current_project,
            widget_options={}
        )


    """
    title = kw.pop("title", "")
    query_func = kw.pop("query_func", get_projects_from_request)
    widget_options = kw.pop("widget_options", {})
    return colander.SchemaNode(
        colander.Integer(),
        title=title,
        missing=colander.required,
        widget=get_deferred_project_select(query_func=query_func, **widget_options),
        validator=get_deferred_project_select_validator(query_func),
        **kw,
    )
