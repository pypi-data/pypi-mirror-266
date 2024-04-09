from caerp.views.payment.invoice import InvoicePaymentAddView

from ..forms.tasks.payment import get_sap_payment_schema


class SAPInvoicePaymentAddView(InvoicePaymentAddView):
    @staticmethod
    def schema_factory(*args, **kwargs):
        return get_sap_payment_schema(*args, **kwargs)


def includeme(config):
    config.add_view(
        SAPInvoicePaymentAddView,
        route_name="/invoices/{id}/addpayment",
        permission="add_payment.invoice",
        renderer="base/formpage.mako",
    )
