import logging
from sqlalchemy import inspect
from caerp.models.supply import (
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierOrder,
    SupplierOrderLine,
    InternalSupplierInvoice,
)
from caerp.utils.strings import format_amount
from caerp.forms.supply.supplier_invoice import (
    get_supplier_invoice_edit_schema,
    validate_supplier_invoice,
)

from ..base_rest_api import (
    BaseRestSupplierDocumentView,
    BaseRestLineView,
    BaseSupplierValidationStatusView,
    SupplierStatusLogEntryRestView,
)
from ..utils import get_supplier_doc_url
from .routes import (
    API_COLLECTION_ROUTE,
    API_ITEM_ROUTE,
    API_LINE_COLLECTION_ROUTE,
    API_LINE_ITEM_ROUTE,
    API_STATUS_LOG_ENTRIES_ROUTE,
    API_STATUS_LOG_ENTRY_ITEM_ROUTE,
)


logger = logging.getLogger(__name__)


class RestSupplierInvoiceView(BaseRestSupplierDocumentView):
    model_class = SupplierInvoice

    def get_schema(self, submited):
        return get_supplier_invoice_edit_schema(self.context.internal)

    def post_format(self, entry, edit, attributes):
        entry = super(RestSupplierInvoiceView, self).post_format(
            entry, edit, attributes
        )
        history = inspect(entry).attrs.supplier_orders.history
        lines_query = SupplierInvoiceLine.query().filter_by(
            supplier_invoice_id=entry.id,
        )

        if history.deleted is not None:
            removed_orders_ids = [i.id for i in history.deleted]
            delete_query = lines_query.join("source_supplier_order_line").filter(
                SupplierOrderLine.supplier_order_id.in_(removed_orders_ids),
            )
            lines_to_delete = SupplierInvoiceLine.query().filter(
                SupplierInvoiceLine.id.in_([i.id for i in delete_query])
            )
            if lines_to_delete.count() > 0:
                lines_to_delete.delete(synchronize_session="fetch")

        if (history.added is not None) and (len(history.added) > 0):
            for order in history.added:
                entry.import_lines_from_order(order)

            entry.supplier_id = history.added[0].supplier_id
            entry.cae_percentage = history.added[0].cae_percentage

        return entry

    def _get_form_sections(self):
        editable = bool(self.request.has_permission("edit.supplier_invoice"))
        has_orders = bool(self.context.supplier_orders)
        sections = {
            "general": {
                "edit": editable,
                "date": {"edit": editable},
                "remote_invoice_number": {"edit": editable},
                "supplier_id": {"edit": not has_orders and editable},
                "cae_percentage": {"edit": not has_orders and editable},
                "payer_id": {},
                "supplier_orders": {"edit": editable},
            },
            "lines": {
                "edit": editable,
                "add": editable,
                "delete": editable,
                "ht": {"edit": editable},
                "tva": {"edit": editable},
            },
        }
        return sections

    def _get_other_actions(self):
        """
        Return the description of other available actions :
            duplicate
            ...
        """
        result = []
        if self.request.has_permission("delete.supplier_invoice"):
            result.append(self._delete_btn())

        if self.request.has_permission("duplicate.supplier_invoice"):
            result.append(self._duplicate_btn())

        if self.request.has_permission("add_payment.supplier_invoice"):
            if (
                self.context.cae_percentage > 0
                and self.context.supplier_paid_status != "resulted"
            ):
                result.append(self._supplier_payment_btn())
            if (
                self.context.cae_percentage < 100
                and self.context.worker_paid_status != "resulted"
            ):
                result.append(self._user_payment_btn())

        return result

    def _get_duplicate_targets_options(self):
        """
        Build the option list to target on which document we want to duplicate
        a line.
        """
        query = self.get_writable_instances()
        result = [
            {
                "label": "{}{}".format(
                    invoice.name,
                    " (facture courante)" if invoice == self.context else "",
                ),
                "id": invoice.id,
            }
            for invoice in query
        ]
        return result

    def _get_supplier_orders_options(self):
        # Returns available orders that belongs to the invoice company
        query = SupplierOrder.query().filter(
            SupplierOrder.company_id == self.context.company_id,
            (
                (SupplierOrder.supplier_invoice_id == self.context.id)
                | (SupplierOrder.supplier_invoice_id == None)  # noqa
            ),
        )

        result = [
            {
                "label": "{} ({}€ TTC)".format(
                    order.name, format_amount(order.total, grouping=False)
                ),
                "id": order.id,
                "supplier_id": order.supplier_id,
            }
            for order in query
        ]
        return result

    def _get_payers_options(self):
        assert isinstance(self.context, SupplierInvoice)

        # Returns active users or currently selected user
        for emp in self.context.company.employees:
            if (emp.login and emp.login.active) or (emp == self.context.payer):
                yield dict(label=emp.label, value=emp.id)

    def _add_form_options(self, form_config):
        form_config = super(RestSupplierInvoiceView, self)._add_form_options(
            form_config,
        )
        invoices_options = self._get_duplicate_targets_options()
        orders_options = self._get_supplier_orders_options()
        suppliers_options = self._get_suppliers_options()
        payers_options = list(self._get_payers_options())

        form_config["options"]["supplier_invoices"] = invoices_options
        form_config["options"]["supplier_orders"] = orders_options
        form_config["options"]["suppliers"] = suppliers_options
        form_config["options"]["payers"] = payers_options

        return form_config

    def _supplier_payment_btn(self):
        url = get_supplier_doc_url(
            self.request,
            suffix="add_supplier_payment",
        )
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Enregistrer un paiement fournisseur",
                "label": "Payer le fournisseur",
                "css": "btn icon btn-primary",
                "icon": "euro-circle",
            },
        }

    def _user_payment_btn(self):
        url = get_supplier_doc_url(
            self.request,
            suffix="add_user_payment",
        )
        return {
            "widget": "anchor",
            "option": {
                "url": url,
                "title": "Enregistrer un remboursement entrepreneur",
                "label": "Rembourser l'entrepreneur",
                "css": "btn icon btn-primary",
                "icon": "euro-circle",
            },
        }


class RestInternalSupplierInvoiceView(RestSupplierInvoiceView):
    def _get_suppliers_options(self):
        return [
            {
                "label": self.context.supplier.label,
                "value": self.context.supplier_id,
            }
        ]

    def _add_form_options(self, form_config):
        form_config = BaseRestSupplierDocumentView._add_form_options(self, form_config)
        form_config["options"]["supplier_orders"] = []
        form_config["options"]["suppliers"] = []
        form_config["options"]["supplier_invoices"] = []
        form_config["options"]["payers"] = []
        return form_config

    def _get_form_sections(self):
        sections = RestSupplierInvoiceView._get_form_sections(self)
        sections["lines"]["add"] = False
        sections["lines"]["delete"] = False
        sections["lines"]["ht"]["edit"] = False
        sections["lines"]["tva"]["edit"] = False
        sections["general"]["date"]["edit"] = False
        sections["general"]["remote_invoice_number"]["edit"] = False
        sections["general"].pop("supplier_id")
        sections["general"].pop("cae_percentage")
        sections["general"].pop("payer_id")
        sections["general"]["supplier_orders"]["edit"] = False
        return sections


class RestSupplierInvoiceLineView(BaseRestLineView):
    model_class = SupplierInvoiceLine
    fk_field_to_container = "supplier_invoice_id"
    duplicate_permission = "edit.supplier_invoice"


class RestSupplierInvoiceValidationStatusView(BaseSupplierValidationStatusView):
    validation_function = staticmethod(validate_supplier_invoice)

    def get_redirect_url(self):
        return get_supplier_doc_url(self.request)


def includeme(config):
    """
    Add rest api views
    """

    config.add_rest_service(
        RestSupplierInvoiceView,
        API_ITEM_ROUTE,
        collection_route_name=API_COLLECTION_ROUTE,
        view_rights="view.supplier_invoice",
        add_rights="add.supplier_invoice",
        edit_rights="edit.supplier_invoice",
        delete_rights="delete.supplier_invoice",
    )

    # Form configuration view
    config.add_view(
        RestSupplierInvoiceView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        permission="view.supplier_invoice",
        context=SupplierInvoice,
    )
    config.add_view(
        RestInternalSupplierInvoiceView,
        attr="form_config",
        route_name=API_ITEM_ROUTE,
        renderer="json",
        request_param="form_config",
        permission="view.supplier_invoice",
        context=InternalSupplierInvoice,
    )

    # # Status view
    config.add_view(
        RestSupplierInvoiceValidationStatusView,
        route_name=API_ITEM_ROUTE,
        request_param="action=validation_status",
        # More fine permission is checked in-view
        permission="view.supplier_invoice",
        request_method="POST",
        renderer="json",
    )

    # Line views
    config.add_rest_service(
        RestSupplierInvoiceLineView,
        API_LINE_ITEM_ROUTE,
        collection_route_name=API_LINE_COLLECTION_ROUTE,
        view_rights="view.supplier_invoice",
        add_rights="edit.supplier_invoice",
        edit_rights="edit.supplier_invoice",
        delete_rights="delete.supplier_invoice",
    )
    config.add_view(
        RestSupplierInvoiceLineView,
        attr="duplicate",
        route_name=API_LINE_ITEM_ROUTE,
        request_param="action=duplicate",
        permission="duplicate.supplier_invoice",
        request_method="POST",
        renderer="json",
    )
    config.add_rest_service(
        SupplierStatusLogEntryRestView,
        API_STATUS_LOG_ENTRY_ITEM_ROUTE,
        collection_route_name=API_STATUS_LOG_ENTRIES_ROUTE,
        collection_view_rights="view.supplier_invoice",
        add_rights="view.supplier_invoice",
        view_rights="view.statuslogentry",
        edit_rights="edit.statuslogentry",
        delete_rights="delete.statuslogentry",
    )
