from caerp.views import redirect_to_index_view

COLLECTION_ROUTE = "/companies"
ITEM_ROUTE = "/companies/{id}"
DASHBOARD_ROUTE = "/companies/{id}/dashboard"
OLD_DASHBOARD_ROUTE = "/company/{id}/dashboard"

API_ROUTE = "/api/v1/companies/"
API_ITEM_ROUTE = "/api/v1/companies/{id}"

COMPANY_ESTIMATIONS_ROUTE = "/companies/{id}/estimations"
COMPANY_ESTIMATION_ADD_ROUTE = "/companies/{id}/estimations/add"
COMPANY_INVOICES_ROUTE = "/companies/{id}/invoices"
COMPANY_INVOICE_ADD_ROUTE = "/companies/{id}/invoices/add"


def includeme(config):
    """
    Configure routes for this module
    """
    config.add_route(COLLECTION_ROUTE, COLLECTION_ROUTE)
    config.add_view(redirect_to_index_view, route_name=OLD_DASHBOARD_ROUTE)
    config.add_route(API_ROUTE, API_ROUTE)

    traverse = "/companies/{id}"
    for route in (
        ITEM_ROUTE,
        DASHBOARD_ROUTE,
        OLD_DASHBOARD_ROUTE,
        COMPANY_ESTIMATIONS_ROUTE,
        COMPANY_ESTIMATION_ADD_ROUTE,
        COMPANY_INVOICES_ROUTE,
        COMPANY_INVOICE_ADD_ROUTE,
        API_ITEM_ROUTE,
    ):
        config.add_route(route, route, traverse=traverse)

    # factorizing those views and thus loosing the match of \d+ makes deletion of statuslogentry to fail (404)
    config.add_route(
        "/api/v1/companies/{id}/statuslogentries",
        r"/api/v1/companies/{id:\d+}/statuslogentries",
        traverse="/companies/{id}",
    )

    config.add_route(
        "/api/v1/companies/{eid}/statuslogentries/{id}",
        r"/api/v1/companies/{eid:\d+}/statuslogentries/{id:\d+}",
        traverse="/statuslogentries/{id}",
    )
