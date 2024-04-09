def includeme(config):
    config.add_route(
        "supplier",
        "/suppliers/{id}",
        traverse="/suppliers/{id}",
    )
    config.add_route(
        "supplier_running_orders",
        "/suppliers/{id}/running_orders",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "supplier_invoiced_orders",
        "/suppliers/{id}/invoiced_orders",
        traverse="/suppliers/{id}",
    )
    config.add_route(
        "supplier_invoices",
        "/suppliers/{id}/invoices",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "supplier_expenselines",
        "/suppliers/{id}/expenselines",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "/api/v1/companies/{id}/suppliers",
        "/api/v1/companies/{id}/suppliers",
        traverse="/companies/{id}",
    )
    config.add_route(
        "/api/v1/suppliers/{id}",
        "/api/v1/suppliers/{id}",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "/api/v1/suppliers/{id}/statuslogentries",
        r"/api/v1/suppliers/{id:\d+}/statuslogentries",
        traverse="/suppliers/{id}",
    )

    config.add_route(
        "/api/v1/suppliers/{eid}/statuslogentries/{id}",
        r"/api/v1/suppliers/{eid:\d+}/statuslogentries/{id:\d+}",
        traverse="/statuslogentries/{id}",
    )

    config.add_route(
        "company_suppliers",
        r"/company/{id:\d+}/suppliers",
        traverse="/companies/{id}",
    )

    config.add_route(
        "suppliers.csv", r"/company/{id:\d+}/suppliers.csv", traverse="/companies/{id}"
    )
    for i in range(2):
        index = i + 1
        route_name = "company_suppliers_import_step%d" % index
        path = r"/company/{id:\d+}/suppliers/import/%d" % index
        config.add_route(route_name, path, traverse="/companies/{id}")
