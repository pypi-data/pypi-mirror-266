from caerp.models.task import InternalInvoice
from caerp.views.invoices.rest_api import (
    InvoiceRestView,
    InvoiceStatusRestView,
    TaskLineGroupRestView,
    DiscountLineRestView,
)
from caerp.views.task.rest_api import (
    TaskFileRequirementRestView,
)


class InternalInvoiceRestView(InvoiceRestView):
    pass


def includeme(config):
    config.add_rest_service(
        InternalInvoiceRestView,
        "/api/v1/invoices/{id}",
        collection_route_name=None,
        edit_rights="edit.invoice",
        view_rights="view.invoice",
        delete_rights="delete.invoice",
        context=InternalInvoice,
    )
    # Form configuration view
    config.add_view(
        InternalInvoiceRestView,
        attr="form_config",
        route_name="/api/v1/invoices/{id}",
        renderer="json",
        request_param="form_config",
        permission="view.invoice",
        context=InternalInvoice,
    )
    # Status View
    config.add_view(
        InvoiceStatusRestView,
        route_name="/api/v1/invoices/{id}",
        request_param="action=status",
        permission="edit.invoice",
        request_method="POST",
        renderer="json",
        context=InternalInvoice,
    )

    # Task linegroup views
    config.add_rest_service(
        TaskLineGroupRestView,
        collection_route_name="/api/v1/invoices/{id}/task_line_groups",
        view_rights="view.invoice",
        add_rights="edit.invoice",
        edit_rights="edit.invoice",
        delete_rights="edit.invoice",
        collection_context=InternalInvoice,
    )
    config.add_view(
        TaskLineGroupRestView,
        route_name="/api/v1/invoices/{id}/task_line_groups",
        attr="post_load_groups_from_catalog_view",
        request_param="action=load_from_catalog",
        request_method="POST",
        renderer="json",
        permission="edit.invoice",
        context=InternalInvoice,
    )
    # Discount line views
    config.add_rest_service(
        DiscountLineRestView,
        collection_route_name="/api/v1/invoices/{id}/discount_lines",
        view_rights="view.invoice",
        add_rights="edit.invoice",
        collection_context=InternalInvoice,
    )
    config.add_view(
        DiscountLineRestView,
        route_name="/api/v1/invoices/{id}/discount_lines",
        attr="post_percent_discount_view",
        request_param="action=insert_percent",
        request_method="POST",
        renderer="json",
        permission="edit.invoice",
        context=InternalInvoice,
    )
    # File requirements views
    config.add_rest_service(
        TaskFileRequirementRestView,
        collection_route_name="/api/v1/invoices/{id}/file_requirements",
        collection_view_rights="view.invoice",
        collection_context=InternalInvoice,
    )
