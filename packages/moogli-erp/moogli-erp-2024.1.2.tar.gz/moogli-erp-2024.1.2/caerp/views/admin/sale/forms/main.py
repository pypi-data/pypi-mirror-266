"""
Configuration générale du module vente:

    Mise en forme des PDFs
    Unité de prestation
"""
import logging
import os

from caerp.models.task import (
    WorkUnit,
    PaymentConditions,
)
from caerp.models.payments import (
    PaymentMode,
)
from caerp.forms.admin import get_config_schema

from caerp.views.admin.tools import (
    get_model_admin_view,
)

from caerp.views.admin.tools import (
    BaseConfigView,
)
from . import FORMS_URL, FormsIndexView


logger = logging.getLogger(__name__)


FORM_CONFIG_URL = os.path.join(FORMS_URL, "config")


class SaleFormAdminView(BaseConfigView):
    title = "Options de formulaire"
    description = (
        "Activation du mode TTC, valeur par défaut limite de validité des devis"
    )
    route_name = FORM_CONFIG_URL
    validation_msg = "Les informations ont bien été enregistrées"

    keys = (
        "task_display_units_default",
        "task_display_ttc_default",
        "estimation_validity_duration_default",
    )
    schema = get_config_schema(keys)


BaseWorkUnitAdminView = get_model_admin_view(WorkUnit, r_path=FORMS_URL)


class WorkUnitAdminView(BaseWorkUnitAdminView):
    disable = False


BasePaymentModeAdminView = get_model_admin_view(PaymentMode, r_path=FORMS_URL)


class PaymentModeAdminView(BasePaymentModeAdminView):
    disable = False


PaymentConditionsAdminView = get_model_admin_view(
    PaymentConditions,
    r_path=FORMS_URL,
)


def includeme(config):
    for view in (
        SaleFormAdminView,
        WorkUnitAdminView,
        PaymentModeAdminView,
        PaymentConditionsAdminView,
    ):
        config.add_route(view.route_name, view.route_name)
        config.add_admin_view(view, parent=FormsIndexView)
