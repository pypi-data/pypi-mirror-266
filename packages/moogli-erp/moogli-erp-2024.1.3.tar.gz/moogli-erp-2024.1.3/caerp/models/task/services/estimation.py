import logging

from caerp_base.models.base import DBSESSION
from caerp.compute.math_utils import convert_to_int, floor_to_precision
from .task import (
    InternalProcessService,
    TaskService,
)


logger = logging.getLogger(__name__)


class EstimationService(TaskService):
    @classmethod
    def create(cls, request, customer, data: dict, no_price_study: bool = False):
        estimation = super().create(request, customer, data, no_price_study)
        estimation.add_default_payment_line()
        estimation.set_default_validity_duration()
        return estimation

    @classmethod
    def cache_totals(cls, request, task_obj):
        result = super().cache_totals(request, task_obj)
        task_obj.update_payment_lines(request)
        return result

    @classmethod
    def get_customer_task_factory(cls, customer):
        from caerp.models.task import InternalEstimation
        from caerp.models.task import Estimation

        if customer.is_internal():
            factory = InternalEstimation
        else:
            factory = Estimation
        return factory

    @classmethod
    def _duplicate_lines(cls, request, original, created):
        super()._duplicate_lines(request, original, created)

        for line in original.payment_lines:
            created.payment_lines.append(line.duplicate())
        return created

    @classmethod
    def duplicate(cls, request, original, user, **kw):
        estimation = super(EstimationService, cls).duplicate(
            request, original, user, **kw
        )

        for field in (
            "deposit",
            "manualDeliverables",
            "paymentDisplay",
            "validity_duration",
        ):
            value = getattr(original, field)
            setattr(estimation, field, value)

        cls.post_duplicate(request, original, estimation, user, **kw)
        return estimation

    @classmethod
    def _clean_payment_lines(cls, estimation, session, payment_times):
        """
        Clean payment lines that should be removed
        """
        payment_lines = list(estimation.payment_lines)
        # Ici on utilise une variable intermédiaire pour éviter
        # les interférences entre la boucle et le pop
        iterator = tuple(enumerate(payment_lines[:-1]))
        for index, line in iterator:
            if index >= payment_times - 1:
                estimation.payment_lines.remove(line)
        return estimation.payment_lines

    @classmethod
    def _complete_payment_lines(cls, estimation, session, payment_times):
        """
        Complete the list of the payment lines to match the number of payments
        """
        from caerp.models.task.estimation import PaymentLine

        payment_lines = cls._clean_payment_lines(estimation, session, payment_times)
        num_lines = len(payment_lines)

        if num_lines < payment_times:
            if num_lines == 0:
                estimation.add_default_payment_line()
                payment_lines = estimation.payment_lines
                num_lines = 1
            sold_line = payment_lines[-1]
            # On s'assure de l'ordre des lignes
            for order, line in enumerate(payment_lines[:-1]):
                line.order = order
                session.merge(line)
            # On crée les lignes qui manquent entre le solde et la dernière échéance
            index = 0
            for index in range(num_lines - 1, payment_times - 1):
                line = PaymentLine(
                    description="Paiement {}".format(index + 1),
                    amount=0,
                    order=index,
                )
                estimation.payment_lines.insert(index, line)
            sold_line.order = index + 1
            session.merge(sold_line)
        elif num_lines != payment_times:
            raise Exception("Erreur dans le code")
        return payment_lines

    @classmethod
    def _update_sold(cls, estimation, session, topay):
        """
        Update the last payment line of an estimation
        """
        payments_sum = 0
        for index, line in enumerate(estimation.payment_lines[:-1]):
            line.order = index
            payments_sum += line.amount
            session.merge(line)
        last_line = estimation.payment_lines[-1]
        last_line.amount = topay - payments_sum
        session.merge(last_line)

    @classmethod
    def _update_computed_payment_lines(cls, estimation, session, payment_times, topay):
        """
        Update the computed payment lines
        """
        lines = cls._complete_payment_lines(estimation, session, payment_times)
        sold_amount = topay
        if payment_times > 1:
            part = int(topay / payment_times)
            part = floor_to_precision(part)
            for line in lines[:-1]:
                line.amount = part
                session.merge(line)
                sold_amount -= part

        sold_line = lines[-1]
        sold_line.amount = sold_amount
        logger.debug("    + The sold amount is {}".format(sold_amount))
        session.merge(sold_line)

        return lines

    @classmethod
    def update_payment_lines(cls, estimation, request, payment_times=None):
        """
        Update the payment lines

        :param obj estimation: Estimation instance

        provided params are used to know what to update, we use the estimation's
        attributes
        """
        logger.debug("Update payment lines")
        if request is None:
            session = DBSESSION()
        else:
            session = request.dbsession
        session.refresh(estimation)
        total = estimation.total()
        logger.debug("   + Total TTC {}".format(total))
        deposit = estimation.deposit_amount_ttc()
        logger.debug("   + Deposit TTC {}".format(deposit))
        topay = total - deposit
        logger.debug("   + Topay after deposit {}".format(topay))

        if estimation.manualDeliverables == 1:
            cls._update_sold(estimation, session, topay)
        else:
            if payment_times is None:
                payment_times = max(len(estimation.payment_lines), 1)
            cls._update_computed_payment_lines(
                estimation, session, payment_times, topay
            )
        session.flush()

    @classmethod
    def on_before_commit(cls, request, task, action: str, changes: dict):
        super().on_before_commit(request, task, action, changes)
        if action == "update":
            if "payment_times" in changes or "deposit" in changes:
                payment_times = changes.get("payment_times", None)
                payment_times = convert_to_int(payment_times, default=None)
                cls.update_payment_lines(task, request, payment_times)
        return task


class EstimationInvoicingService:
    """
    Service managing invoice generation for estimations
    """

    @classmethod
    def _get_common_invoice(cls, request, estimation, user):
        """
        Prepare a new Invoice related to the given estimation

        :param obj estimation: The estimation we're starting from
        :param obj user: The user generating the new document
        :returns: A new Invoice/InternalInvoice
        :rtype: `class:Invoice`
        """
        params = dict(
            user=user,
            company=estimation.company,
            project=estimation.project,
            phase_id=estimation.phase_id,
            estimation=estimation,
            payment_conditions=estimation.payment_conditions,
            description=estimation.description,
            address=estimation.address,
            workplace=estimation.workplace,
            mentions=[mention for mention in estimation.mentions if mention.active],
            business_type_id=estimation.business_type_id,
            notes=estimation.notes,
            mode=estimation.mode,
            display_ttc=estimation.display_ttc,
            start_date=estimation.start_date,
            end_date=estimation.end_date,
            first_visit=estimation.first_visit,
            decimal_to_display=estimation.decimal_to_display,
            insurance_id=estimation.insurance_id,
            business_id=estimation.business_id,
        )
        from caerp.models.task.services.invoice import InvoiceService

        invoice = InvoiceService._new_instance(request, estimation.customer, params)
        return invoice

    @classmethod
    def _get_task_line(cls, cost, description, tva):
        from caerp.models.task.task import TaskLine
        from caerp.models.tva import Product

        line = TaskLine(cost=cost, description=description, tva=tva, quantity=1)
        line.product_id = Product.first_by_tva_value(tva)
        return line

    @classmethod
    def _get_deposit_task_line(cls, cost, tva):
        """
        Return an deposit invoiceline
        """
        description = "Facture d'acompte"
        return cls._get_task_line(cost, description, tva)

    @classmethod
    def _get_deposit_task_lines(cls, estimation):
        """
        Return all deposit invoiceline
        """
        lines = []
        for tva, cost in list(estimation.deposit_amounts_native().items()):
            line = cls._get_deposit_task_line(cost, tva)
            lines.append(line)
        return lines

    @classmethod
    def gen_deposit_invoice(cls, request, estimation, user):
        """
        Generate a deposit invoice based on the given estimation

        :param obj estimation: The estimation we're starting from
        :param obj user: The user generating the new document
        :returns: A new Invoice / InternalInvoice
        :rtype: `class:Invoice`
        """
        invoice = cls._get_common_invoice(request, estimation, user)
        invoice.financial_year = invoice.date.year
        invoice.display_units = 0
        invoice.default_line_group.lines.extend(cls._get_deposit_task_lines(estimation))
        invoice.fix_lines_mode()
        invoice.cache_totals(request)
        return invoice

    @classmethod
    def _get_intermediate_invoiceable_amounts(cls, estimation):
        """
        Collect the amounts that should be invoiced in each intermediate
        payment deadline

        :param obj estimation: The estimation we're working on
        :returns: The amounts to be invoiced in form of a list of dict
        [{tva1: 10, tva2: 15}]
        :rtype: list
        """
        if estimation.manualDeliverables == 1:
            # On fait le calcul globale de tous les paiements et on récupère
            # celui que l'on veut
            payments = estimation.manual_payment_line_amounts()[:-1]
        else:
            divided_amount = estimation.paymentline_amounts_native()
            # All but not the last one (sold)
            num_payments = len(estimation.payment_lines) - 1
            payments = [divided_amount for i in range(num_payments)]
        return payments

    @classmethod
    def _get_intermediate_task_lines(cls, payment_line, payment_description):
        lines = []
        for tva, cost in list(payment_description.items()):
            line = cls._get_task_line(cost, payment_line.description, tva)
            lines.append(line)
        return lines

    @classmethod
    def gen_intermediate_invoice(cls, request, estimation, payment_line, user):
        """
        Generate an intermediate invoice based on the given payment_line
        definition

        :param obj estimation: The estimation we're starting from
        :param obj payment_line: The PaymentLine describing the invoice
        :param obj user: The user generating the new document
        :returns: A new Invoice/InternalInvoice object
        :rtype: `class:Invoice`
        """
        line_index = estimation.payment_lines[:-1].index(payment_line)

        invoice = cls._get_common_invoice(request, estimation, user)
        if invoice.date < payment_line.date:
            invoice.date = payment_line.date
        invoice.financial_year = invoice.date.year
        invoice.display_units = 0

        payments = cls._get_intermediate_invoiceable_amounts(estimation)
        payment_description = payments[line_index]

        invoice.default_line_group.lines.extend(
            cls._get_intermediate_task_lines(
                payment_line,
                payment_description,
            )
        )
        invoice.fix_lines_mode()
        invoice.cache_totals(request)
        return invoice

    @classmethod
    def _get_all_intermediate_invoiceable_task_lines(cls, estimation):
        """
        Build all intermediate invoiceable task lines including the deposit

        :param obj estimation: The estimation we're working on
        :returns: A list with all task lines
        :rtype: list of `class:TaskLine` instances
        """
        payment_descriptions = cls._get_intermediate_invoiceable_amounts(estimation)
        payments = estimation.payment_lines[:-1]

        result = []
        if estimation.deposit:
            result.extend(cls._get_deposit_task_lines(estimation))

        for payment, description in zip(payments, payment_descriptions):
            result.extend(cls._get_intermediate_task_lines(payment, description))
        return result

    @classmethod
    def gen_sold_price_study(
        cls, request, estimation, invoice, intermediate_task_lines
    ):
        """
        Generate a price study attached to the sold invoice compiling
        the estimation informations and the intermediary invoices
        """
        from caerp.models.price_study import PriceStudyChapter, PriceStudyProduct
        from caerp.models.tva import Tva

        # On crée une étude de prix sans les éléments de calcul (coef de marge
        # ...)
        price_study = estimation.price_study.duplicate(force_ht=True)
        price_study.task = invoice

        # On crée des produits d'étude pour acompte + paiements intermédiaires
        if intermediate_task_lines:
            chapter = PriceStudyChapter()
            request.dbsession.add(chapter)
            price_study.chapters.append(chapter)
            for line in intermediate_task_lines:
                product = PriceStudyProduct(
                    chapter=chapter,
                    description=line.description,
                    ht=-1 * line.cost,
                    tva=Tva.by_value(line.tva),
                    quantity=1,
                )
                request.dbsession.add(product)

        request.dbsession.flush()

        # On synchronise les montants
        price_study.sync_amounts(sync_down=True)
        # On synchronise la facture avec les données de l'étude
        price_study.sync_with_task(request)

        return price_study

    @classmethod
    def gen_sold_invoice(cls, request, estimation, user):
        """
        Generate a sold invoice based on the given estimation definition

        :param obj estimation: The estimation we're starting from
        :param obj user: The user generating the new document
        :returns: A new Invoice/Internal object
        :rtype: `class:Invoice`
        """
        payment_line = estimation.payment_lines[-1]
        invoice = cls._get_common_invoice(request, estimation, user)

        if invoice.date < payment_line.date:
            invoice.date = payment_line.date
        invoice.financial_year = invoice.date.year
        invoice.display_units = estimation.display_units
        invoice.expenses_ht = estimation.expenses_ht
        line_groups = []
        # Retrieve already invoiced lines
        task_lines = cls._get_all_intermediate_invoiceable_task_lines(estimation)

        if estimation.has_price_study():
            # On génère une étude de prix (sans les formules de calcul, direct en ht)
            # Et on génère les TaskLineGroup et TaskLine depuis l'étude
            invoice._clean_task(request)
            cls.gen_sold_price_study(request, estimation, invoice, task_lines)
        else:
            for group in estimation.line_groups:
                line_groups.append(group.duplicate())

            if task_lines:
                if len(line_groups) > 1:
                    from caerp.models.task.task import TaskLineGroup

                    already_invoiced_group = TaskLineGroup()
                    line_groups.append(already_invoiced_group)
                else:
                    already_invoiced_group = line_groups[0]

                task_lines.reverse()
                current_order = len(already_invoiced_group.lines)
                for line in task_lines:
                    current_order += 1
                    line.cost = -1 * line.cost
                    line.order = current_order
                    already_invoiced_group.lines.append(line)

            for discount in estimation.discounts:
                invoice.discounts.append(discount.duplicate())

            invoice.line_groups = line_groups
            invoice.fix_lines_mode()
            invoice.cache_totals(request)
        return invoice


class InternalEstimationService(EstimationService):
    pass


class InternalEstimationInvoicingService(EstimationInvoicingService):
    pass


class InternalEstimationProcessService(InternalProcessService):
    @classmethod
    def _generate_supplier_document(cls, document, request, supplier):
        logger.debug(
            "  + Generate a supplier order document for {}".format(document.id)
        )
        from caerp_base.models.base import DBSESSION
        from caerp.models.supply.internalsupplier_order import (
            InternalSupplierOrder,
        )

        order = InternalSupplierOrder.from_estimation(document, supplier)
        order.supplier = supplier
        DBSESSION().add(order)
        file_ = document.pdf_file.duplicate()
        file_.parent_id = order.id
        DBSESSION().merge(file_)
        document.supplier_order = order
        DBSESSION().merge(document)
        DBSESSION().flush()
        logger.debug("  + Done")
        return order
