import deform_extensions
import deform
import colander
from functools import partial
from colanderalchemy import SQLAlchemySchemaNode


from caerp import forms
from caerp_base.models.base import DBSESSION
from caerp.models.services.bpf import BPFService
from caerp.models.task.invoice import get_invoice_years, Invoice


# Layouts
INCOME_SOURCE_GRID = (
    (
        ("invoice_id", 6),
        ("income_category_id", 6),
    ),
)
TRAINEE_TYPE_GRID = (
    (
        ("trainee_type_id", 6),
        ("headcount", 3),
        ("total_hours", 3),
    ),
)
BPF_DATA_GRID = [
    (
        ("financial_year", 6),
        ("cerfa_version", 6),
    ),
    (
        ("headcount", 6),
        ("total_hours", 6),
    ),
    (("trainee_types", 12),),
    (("remote_headcount", 12),),
    (
        ("has_subcontract", 6),
        ("has_subcontract_amount", 2),
        ("has_subcontract_headcount", 2),
        ("has_subcontract_hours", 2),
    ),
    (("is_subcontract", 6),),
    (("income_sources", 12),),
    (("training_goal_id", 12),),
    (("training_speciality_id", 12),),
]


@colander.deferred
def deferred_nsf_training_speciality_id_widget(node, kw):
    from caerp.models.training.bpf import NSFTrainingSpecialityOption

    query = NSFTrainingSpecialityOption.query()
    query = query.order_by(NSFTrainingSpecialityOption.label)
    values = [(i.id, i.label) for i in query]
    placeholder = "- Sélectionner une spécialité -"
    values.insert(0, ("", placeholder))
    # Use of placeholder arg is mandatory with Select2 ; otherwise, the
    # clear button crashes. https://github.com/select2/select2/issues/5725
    return deform.widget.Select2Widget(values=values, placeholder=placeholder)


def get_year_from_request(request):
    return int(request.matchdict["year"])


def _get_cerfa_spec(request):
    assert request is not None
    year = get_year_from_request(request)
    return BPFService.get_spec_from_year(year)


def _build_select_values(choices_tree):
    """
    Build values suitable for SelectWidget, from a nested list structure

    Example choices_tree (with 1 optgroup and 2 uncategorized items):
        [
            (0, 'soap', []),
            (None, "Vegetables", [
                (1, "carots"),
                (2, "celery"),
            ]),
           (3, 'toilet paper'),
        ]
    """
    values = []
    for source in choices_tree:
        index, source_label, subsources = source

        if len(subsources) == 0:
            values.append([index, source_label])
        else:
            optgroup_values = []
            for subsource_index, subsource_label in subsources:
                optgroup_values.append([subsource_index, subsource_label])
            optgroup = deform.widget.OptGroup(source_label, *optgroup_values)
            values.append(optgroup)
    return values


@colander.deferred
def deferred_income_source_select(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    values = _build_select_values(spec.INCOME_SOURCES)
    values.insert(0, ("", "- Sélectionner une source de revenu -"))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def deferred_income_source_validator(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    return colander.OneOf(spec.get_income_sources_ids())


@colander.deferred
def deferred_training_goal_select(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    values = _build_select_values(spec.TRAINING_GOALS)
    values.insert(0, ("", "- Sélectionner un objectif de formation -"))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def deferred_training_goal_validator(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    return colander.OneOf(spec.get_training_goals_ids())


@colander.deferred
def deferred_trainee_type_select(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    values = _build_select_values(spec.TRAINEE_TYPES)
    values.insert(0, ("", "- Sélectionner un type de stagiaire -"))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def deferred_trainee_type_validator(node, kw):
    spec = _get_cerfa_spec(kw.get("request"))
    return colander.OneOf(spec.get_trainee_types_ids())


@colander.deferred
def deferred_financial_year_validator(node, kw):
    """
    Validate the BPF year

    Validates:
    - existing financial year
    - the year is not already "filled" with in another object
    """
    request = kw.get("request")
    assert request is not None

    business = request.context
    current_bpf_year = int(request.matchdict["year"])

    years_w_bpf_data = [bpf.financial_year for bpf in business.bpf_datas]
    invoicing_years = get_invoice_years()

    def validator(node, value):
        if value not in invoicing_years:
            raise colander.Invalid(
                node,
                "Pas une année fiscale valide",
                value,
            )
        if value in years_w_bpf_data and value != current_bpf_year:
            raise colander.Invalid(
                node,
                "Il y a déjà des données BPF pour cette année",
                value,
            )

    return validator


@colander.deferred
def deferred_invoice_widget(node, kw):
    """
    Return a select for invoice selection
    """
    assert kw["request"] is not None
    query = DBSESSION().query(Invoice.id, Invoice.name)
    query = query.filter_by(business_id=kw["request"].context.id)
    choices = []
    for invoice in query:
        choices.append((invoice.id, invoice.name))
    return deform.widget.SelectWidget(values=choices)


def customize_trainee_types_node(schema):
    """Customize the trainee_types (TraineeCount model) form schema node"""
    schema.widget = deform_extensions.GridMappingWidget(
        named_grid=TRAINEE_TYPE_GRID,
    )
    schema.title = "type de stagiaire"
    customize = partial(forms.customize_field, schema)
    customize(
        "id",
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
    )
    customize(
        "trainee_type_id",
        widget=deferred_trainee_type_select,
        validator=deferred_trainee_type_validator,
    )
    customize("headcount", validator=colander.Range(min=0))
    customize(
        "total_hours",
        validator=colander.Range(min=0),
        description=(
            "Si tous les stagiaires de ce type ont le même volume "
            + "horaire : nb. heures x nb. stagiaires de ce type."
        ),
    )
    return schema


def customize_income_source_node(schema):
    """
    Customize the income_sources form schema node
    Node related to the IncomeSource model
    """
    schema.widget = deform_extensions.GridMappingWidget(
        named_grid=INCOME_SOURCE_GRID,
    )
    schema.title = "financement"

    customize = partial(forms.customize_field, schema)
    customize(
        "id",
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
    )
    customize("invoice_id", widget=deferred_invoice_widget)
    customize(
        "income_category_id",
        widget=deferred_income_source_select,
        validator=deferred_income_source_validator,
    )

    return schema


def customize_bpf_schema(schema: SQLAlchemySchemaNode) -> SQLAlchemySchemaNode:
    """Complete the schema generated from the model with
    specific form customization
    """
    schema.widget = deform_extensions.GridFormWidget(named_grid=BPF_DATA_GRID)
    customize = partial(forms.customize_field, schema)
    customize(
        "id",
        widget=deform.widget.HiddenWidget(),
        missing=colander.drop,
    )
    customize(
        "financial_year",
        widget=forms.get_year_select_deferred(
            query_func=get_invoice_years,
        ),
        validator=deferred_financial_year_validator,
    )
    customize(
        "cerfa_version",
        widget=deform.widget.TextInputWidget(readonly=True),
        missing=colander.drop,
    )
    customize(
        "total_hours",
        validator=colander.Range(min=0),
        description="Si tous les stagiaires ont le même volume horaire : nb. heures x nb. stagiaires",
    )
    customize(
        "headcount",
        validator=colander.Range(min=0),
    )
    customize(
        "has_subcontract",
        widget=deform.widget.SelectWidget(
            values=(
                ("no", "Non"),
                ("full", "Totalement"),
                ("part", "Partiellement"),
            ),
            inline=True,
        ),
        description="Correspond à l'achat ou non de formation à un tiers",
    )
    customize(
        "has_subcontract_hours",
        validator=colander.Range(min=0),
    )
    customize("has_subcontract_headcount", validator=colander.Range(min=0))
    customize(
        "has_subcontract_amount",
        description="Dépensé en sous-traitance",
        validator=colander.Range(min=0),
    )
    customize(
        "remote_headcount",
        description="nombre de stagiaires",
        validator=colander.Range(min=0),
    )
    customize(
        "is_subcontract",
        widget=deform.widget.SelectWidget(
            values=(
                ("false", "Oui"),
                (
                    "true",
                    "Non (portée par un autre Organisme "
                    "de formation qui m'achète de la formation "
                    "en sous-traitance)",
                ),
            ),
        ),
    )
    customize(
        "training_speciality_id",
        widget=deferred_nsf_training_speciality_id_widget,
    )
    customize(
        "training_goal_id",
        widget=deferred_training_goal_select,
        validator=deferred_training_goal_validator,
    )
    customize(
        "trainee_types",
        widget=deform.widget.SequenceWidget(
            add_subitem_text_template="Renseigner un type de stagiaire supplémentaire",
            min_len=1,
        ),
    )
    child_node = schema["trainee_types"].children[0]
    customize_trainee_types_node(child_node)
    customize(
        "income_sources",
        widget=deform.widget.SequenceWidget(
            add_subitem_text_template="Renseigner un financement supplémentaire",
            min_len=1,
        ),
    )
    child_node = schema["income_sources"].children[0]
    customize_income_source_node(child_node)
    return schema


def get_business_bpf_edit_schema():
    from caerp.models.training.bpf import BusinessBPFData

    schema = SQLAlchemySchemaNode(
        BusinessBPFData,
        excludes=(
            "id",
            "business_id",
            "business",
            "training_speciality",
        ),
    )
    return customize_bpf_schema(schema)
