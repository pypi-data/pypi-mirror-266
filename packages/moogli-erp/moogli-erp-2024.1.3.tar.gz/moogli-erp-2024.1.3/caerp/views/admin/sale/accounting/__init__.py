import os
from caerp.views.admin.sale import (
    SALE_URL,
    SaleIndexView,
)
from caerp.views.admin.tools import BaseAdminIndexView


ACCOUNTING_INDEX_URL = os.path.join(SALE_URL, "accounting")


class SaleAccountingIndex(BaseAdminIndexView):
    title = "Comptabilité : Écritures de ventes"
    description = "Configurer la génération des écritures de vente"
    route_name = ACCOUNTING_INDEX_URL


def includeme(config):
    config.add_route(ACCOUNTING_INDEX_URL, ACCOUNTING_INDEX_URL)
    config.add_admin_view(SaleAccountingIndex, parent=SaleIndexView)
    config.include(".common")
    config.include(".invoice")
    config.include(".internalinvoice")
