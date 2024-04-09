import os

COMPANY_CUSTOMERS_ROUTE = "/companies/{id}/customers"
CUSTOMER_ITEM_ROUTE = "customer"
CUSTOMER_ITEM_ESTIMATION_ROUTE = "/customers/{id}/estimations"
CUSTOMER_ITEM_INVOICE_ROUTE = "/customers/{id}/invoices"
CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE = CUSTOMER_ITEM_INVOICE_ROUTE + ".{extension}"
COMPANY_CUSTOMERS_ADD_ROUTE = os.path.join(COMPANY_CUSTOMERS_ROUTE, "add")

API_COMPANY_CUSTOMERS_ROUTE = "/api/v1/companies/{id}/customers"
CUSTOMER_REST_ROUTE = "/api/v1/customers/{id}"
CUSTOMER_STATUS_LOG_ROUTE = "/api/v1/customers/{id}/statuslogentries"
CUSTOMER_STATUS_LOG_ITEM_ROUTE = "/api/v1/customers/{eid}/statuslogentries/{id}"


def includeme(config):
    route = API_COMPANY_CUSTOMERS_ROUTE
    pattern = r"{}".format(route.replace("id", r"id:\d+"))
    config.add_route(
        route,
        pattern,
        traverse="/companies/{id}",
    )

    config.add_route(
        CUSTOMER_ITEM_ROUTE,
        r"/customers/{id:\d+}",
        traverse="/customers/{id}",
    )
    for route in (
        CUSTOMER_REST_ROUTE,
        CUSTOMER_ITEM_ESTIMATION_ROUTE,
        CUSTOMER_ITEM_INVOICE_ROUTE,
        CUSTOMER_ITEM_INVOICE_EXPORT_ROUTE,
        CUSTOMER_STATUS_LOG_ROUTE,
    ):
        pattern = r"{}".format(route.replace("id", r"id:\d+"))
        config.add_route(
            route,
            pattern,
            traverse="/customers/{id}",
        )

    route = CUSTOMER_STATUS_LOG_ITEM_ROUTE
    pattern = r"{}".format(route.replace("id", r"id:\d+"))
    config.add_route(
        route,
        pattern,
        traverse="/statuslogentries/{id}",
    )

    for route in (COMPANY_CUSTOMERS_ROUTE, COMPANY_CUSTOMERS_ADD_ROUTE):
        pattern = r"{}".format(route.replace("id", r"id:\d+"))
        config.add_route(route, pattern, traverse="/companies/{id}")

    config.add_route(
        "customers.csv", r"/company/{id:\d+}/customers.csv", traverse="/companies/{id}"
    )
