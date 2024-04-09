from caerp.utils.menu import MenuItem
from caerp.utils.widgets import POSTButton, Link

from caerp.views.task.utils import get_task_url, task_pdf_link
from caerp.views.task.layout import TaskLayout, get_task_menu
from caerp.views.invoices.routes import (
    INVOICE_ITEM_ACCOUNTING_ROUTE,
    INVOICE_ITEM_FILES_ROUTE,
    INVOICE_ITEM_GENERAL_ROUTE,
    INVOICE_ITEM_PAYMENT_ROUTE,
    INVOICE_ITEM_PREVIEW_ROUTE,
    CINV_ITEM_GENERAL_ROUTE,
    CINV_ITEM_PREVIEW_ROUTE,
    CINV_ITEM_ACCOUNTING_ROUTE,
    CINV_ITEM_FILES_ROUTE,
)


def invoice_menu(layout_class):
    menu = get_task_menu(
        INVOICE_ITEM_GENERAL_ROUTE, INVOICE_ITEM_PREVIEW_ROUTE, INVOICE_ITEM_FILES_ROUTE
    )
    menu.add_before(
        "task_files",
        MenuItem(
            name="invoice_accounting",
            label="Comptabilité",
            route_name=INVOICE_ITEM_ACCOUNTING_ROUTE,
            icon="file-spreadsheet",
        ),
    )
    menu.add_before(
        "task_files",
        MenuItem(
            name="invoice_payments",
            label="Encaissements",
            route_name=INVOICE_ITEM_PAYMENT_ROUTE,
            icon="euro-circle",
        ),
    )
    return menu


def cancelinvoice_menu(layout_class):
    menu = get_task_menu(
        CINV_ITEM_GENERAL_ROUTE, CINV_ITEM_PREVIEW_ROUTE, CINV_ITEM_FILES_ROUTE
    )
    menu.add_before(
        "task_files",
        MenuItem(
            name="invoice_accounting",
            label="Comptabilité",
            route_name=CINV_ITEM_ACCOUNTING_ROUTE,
            icon="file-spreadsheet",
        ),
    )
    menu.remove("task_files")
    return menu


class InvoiceLayout(TaskLayout):
    menu_factory = invoice_menu

    @property
    def title(self):
        internal = ""
        if self.context.internal:
            internal = "interne "
        if self.context.official_number:
            return (
                f"Facture {internal}N<span class='screen-reader-text'>umér</span>"
                f"<sup>o</sup>{self.context.official_number} avec le client "
                f"{self.context.customer.label}"
            )
        else:
            # Facture en attente de validation (vue entrepreneur)
            return f"Facture {internal} avec le client {self.context.customer.label}"

    def stream_gen_cinv_button(self):
        if self.request.has_permission("gencinv.invoice"):
            if (
                self.context.invoicing_mode == self.context.CLASSIC_MODE
                or self.context.business.get_current_invoice() is None
            ):
                codejs = None
                if self.context.paid_status == "resulted":
                    codejs = "return confirm('Cette facture est déjà soldée. \
Générer un avoir quand même ?')"
                yield POSTButton(
                    get_task_url(self.request, suffix="/gencinv"),
                    label="Avoir",
                    title="Générer un avoir pour cette facture",
                    css="btn icon_only_mobile",
                    icon="plus-circle",
                    js=codejs,
                )

    def stream_main_actions(self):
        if (
            self.request.has_permission("draft.invoice")
            and self.context.status != "draft"
        ):
            yield POSTButton(
                get_task_url(self.request, suffix="/set_draft"),
                label="Repasser en brouillon",
                icon="pen",
                css="btn btn-primary icon_only_mobile",
                title="Repasser cette facture en brouillon pour pouvoir la modifier",
            )

        if self.request.has_permission("add_payment.invoice"):
            yield Link(
                get_task_url(self.request, suffix="/addpayment"),
                label="Encaisser",
                title="Enregistrer un encaissement pour cette facture",
                icon="euro-circle",
                css="btn icon_only_mobile",
            )
        yield from self.stream_gen_cinv_button()

        if self.request.has_permission("set_treasury.invoice"):
            yield Link(
                get_task_url(self.request, suffix="/set_products"),
                label="Codes<span class='no_mobile'>&nbsp;produits</span>",
                title="Configurer les codes produits de cette facture",
                icon="cog",
                css="btn",
            )
        if (
            not self.context.estimation
            and self.context.invoicing_mode == "classic"
            and not self.context.internal
        ):
            yield Link(
                get_task_url(self.request, suffix="/attach_estimation"),
                label="Rattacher à un devis",
                title="Rattacher cette facture à un devis",
                css="btn",
                icon="link",
            )

        if self.request.has_permission("gen_supplier_invoice.invoice"):
            yield POSTButton(
                get_task_url(self.request, suffix="/gen_supplier_invoice"),
                "Facture fournisseur",
                icon="plus",
                title=(
                    "Générer la facture fournisseur dans l'espace de "
                    "l'enseigne {}".format(self.context.customer.label)
                ),
            )

    def stream_more_actions(self):
        if self.request.has_permission("duplicate.invoice"):
            yield Link(
                get_task_url(self.request, suffix="/duplicate"),
                label="",
                title="Dupliquer cette facture",
                icon="copy",
                css="btn icon only",
            )

        yield Link(
            get_task_url(self.request, suffix="/set_metadatas"),
            label="",
            icon="folder-move",
            css="btn icon only",
            title="Déplacer ou renommer cette facture",
        )

        yield task_pdf_link(self.request, "cette facture")


class CancelInvoiceLayout(TaskLayout):
    menu_factory = cancelinvoice_menu

    @property
    def title(self):
        internal = ""
        if self.context.internal:
            internal = "interne "
        return (
            f"Avoir {internal}N<span class='screen-reader-text'>umér</span>"
            f"<sup>o</sup>{self.context.official_number} avec le client "
            f"{self.context.customer.label}"
        )

    def stream_main_actions(self):
        if self.request.has_permission("gen_supplier_invoice.invoice"):
            yield POSTButton(
                get_task_url(self.request, suffix="/gen_supplier_invoice"),
                "Facture fournisseur",
                icon="plus",
                css="btn btn-primary icon_only_mobile",
                title=(
                    "Générer la facture fournisseur dans l'espace de "
                    "l'enseigne {}".format(self.context.customer.label)
                ),
            )
        if (
            self.request.has_permission("draft.cancelinvoice")
            and self.context.status != "draft"
        ):
            yield POSTButton(
                self.request.route_path(
                    "/cancelinvoices/{id}/set_draft", id=self.context.id
                ),
                label="Repasser en brouillon",
                icon="pen",
                css="btn icon_only_mobile",
                title="Repasser cet avoir en brouillon pour pouvoir le modifier",
            )
        if self.request.has_permission("set_treasury.cancelinvoice"):
            yield Link(
                get_task_url(self.request, suffix="/set_products"),
                label="Codes<span class='no_mobile'>&nbsp;produits</span>",
                title="Configurer les codes produits de cet avoir",
                icon="cog",
                css="btn icon_only_mobile",
            )

    def stream_more_actions(self):
        yield Link(
            self.request.route_path(
                "/cancelinvoices/{id}/set_metadatas", id=self.context.id
            ),
            label="",
            icon="folder-move",
            css="btn icon only",
            title="Déplacer ou renommer cet avoir",
        )
        yield task_pdf_link(self.request, "cet avoir")


def includeme(config):
    config.add_layout(
        InvoiceLayout,
        template="caerp:templates/tasks/invoice/layout.mako",
        name="invoice",
    )
    config.add_layout(
        CancelInvoiceLayout,
        template="caerp:templates/tasks/cancelinvoice/layout.mako",
        name="cancelinvoice",
    )
