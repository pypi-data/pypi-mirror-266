def admin_accounting_index_view(request):
    menus = []
    for label, route, title, icon in (
        ("Retour", "admin_index", "", "arrow-left"),
        (
            "Configurer les États de Trésorerie",
            "/admin/accounting/treasury_measures",
            "Les états de trésorerie sont générés depuis les balances "
            "analytiques déposées dans de MooGLi",
            "euro-circle",
        ),
        (
            "Configurer les Comptes de résultat",
            "/admin/accounting/income_statement_measures",
            "Les comptes de résultat sont générés depuis les grands livres "
            "déposés dans de MooGLi",
            "table",
        ),
    ):
        menus.append(dict(label=label, route_name=route, title=title, icon=icon))
    return dict(title="Configuration du module Fichier de trésorerie", menus=menus)


def includeme(config):
    config.add_route("/admin/accounting", "/admin/accounting")
    config.add_admin_view(admin_accounting_index_view, route_name="/admin/accounting")
