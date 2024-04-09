from caerp.views.admin.vente.vente import (
    WorkUnitAdmin,
    TaskMentionAdmin,
    PaymentModeAdmin,
    PaymentConditionAdmin,
)


def admin_vente_index_view(request):
    """
    vue d'index pour la configuration du module vente
    """
    menus = []
    for label, route, title, icon in (
        ("Retour", "admin_index", "", "arrow-left"),
        (WorkUnitAdmin.title, "admin_vente_workunit", WorkUnitAdmin.description, ""),
        (
            TaskMentionAdmin.title,
            "admin_vente_mention",
            TaskMentionAdmin.description,
            "",
        ),
        (
            PaymentModeAdmin.title,
            "admin_vente_payment_mode",
            PaymentModeAdmin.description,
            "",
        ),
        (
            PaymentConditionAdmin.title,
            "admin_vente_payment_condition",
            PaymentConditionAdmin.description,
            "",
        ),
        (
            "Configuration comptable du module Ventes",
            "admin_vente_treasury",
            "Configuration des modules d'exports prédéfinis et personnalisés",
            "",
        ),
        (
            "Configuration comptable des produits et TVA collectés",
            "/admin/vente/tvas",
            "Taux de TVA, codes produit et codes analytiques associés",
            "",
        ),
        (
            "Configuration comptable des encaissements",
            "admin_receipts",
            "Configuration des différents comptes analytiques liés \
aux encaissements",
            "",
        ),
    ):
        menus.append(dict(label=label, route_name=route, title=title, icon=icon))
    return dict(title="Configuration du module Ventes", menus=menus)


def includeme(config):
    config.add_route("admin_vente", "admin/vente")
    config.add_admin_view(
        admin_vente_index_view,
        route_name="admin_vente",
    )
