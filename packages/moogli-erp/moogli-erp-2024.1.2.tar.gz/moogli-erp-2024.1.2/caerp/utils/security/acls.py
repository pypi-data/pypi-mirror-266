"""
    Root factory <=> Acl handling
"""
import logging
import datetime
from pyramid.authorization import (
    Allow,
    Deny,
    Everyone,
    Authenticated,
    ALL_PERMISSIONS,
)
from pyramid.threadlocal import get_current_request
from sqlalchemy.orm import (
    undefer_group,
    load_only,
)
from caerp_base.models.base import DBSESSION
from caerp_celery.models import Job
from caerp.models.services.find_company import FindCompanyService
from caerp.models.config import ConfigFiles
from caerp.models.activity import Activity
from caerp.models.company import Company
from caerp.models.competence import (
    CompetenceGrid,
    CompetenceGridItem,
    CompetenceGridSubItem,
)
from caerp.models.status import StatusLogEntry
from caerp.models.third_party.customer import Customer
from caerp.models.third_party.supplier import Supplier
from caerp.models.files import (
    File,
    Template,
    TemplatingHistory,
)
from caerp.plugins.sap.models.sap import SAPAttestation
from caerp.models.supply import (
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierOrder,
    SupplierOrderLine,
    SupplierInvoiceSupplierPayment,
    SupplierInvoiceUserPayment,
    InternalSupplierInvoice,
    BaseSupplierInvoicePayment,
)
from caerp.models.user.group import Group
from caerp.models.project import (
    Project,
    Phase,
)
from caerp.models.node import Node
from caerp.models.project.types import (
    ProjectType,
    BusinessType,
)
from caerp.models.project.business import Business
from caerp.models.task.task import (
    TaskLine,
    TaskLineGroup,
    DiscountLine,
    PostTTCLine,
    Task,
)
from caerp.models.task.estimation import (
    PaymentLine,
)
from caerp.models.task import (
    Invoice,
    InternalInvoice,
    CancelInvoice,
    InternalCancelInvoice,
    Estimation,
    InternalEstimation,
)
from caerp.models.task import (
    BaseTaskPayment,
    Payment,
    InternalPayment,
    BankRemittance,
)
from caerp.models.task.mentions import TaskMention
from caerp.models.task.insurance import TaskInsuranceOption
from caerp.models.workshop import (
    Workshop,
    Timeslot,
)
from caerp.models.expense.sheet import (
    ExpenseSheet,
    BaseExpenseLine,
)
from caerp.models.expense.payment import ExpensePayment
from caerp.models.expense.types import ExpenseType
from caerp.models.indicators import (
    Indicator,
    CustomBusinessIndicator,
    SaleFileRequirement,
)

from caerp.models.user.login import Login
from caerp.models.user.user import User
from caerp.models.user.userdatas import UserDatas
from caerp.models.training.trainer import TrainerDatas
from caerp.models.statistics import (
    StatisticSheet,
    StatisticEntry,
    StatisticCriterion,
)
from caerp.models.options import ConfigurableOption
from caerp.models.sale_product.base import (
    BaseSaleProduct,
    SaleProductStockOperation,
)
from caerp.models.sale_product.work import SaleProductWork
from caerp.models.sale_product.category import SaleProductCategory
from caerp.models.sale_product.work_item import WorkItem

from caerp.models.price_study import (
    PriceStudy,
    PriceStudyChapter,
    BasePriceStudyProduct,
    PriceStudyWork,
    PriceStudyWorkItem,
    PriceStudyDiscount,
)
from caerp.models.progress_invoicing import (
    ProgressInvoicingPlan,
    ProgressInvoicingChapter,
    ProgressInvoicingBaseProduct,
    ProgressInvoicingWorkItem,
)

from caerp.models.tva import Tva
from caerp.models.career_stage import CareerStage
from caerp.models.career_path import CareerPath
from caerp.models.accounting.operations import (
    AccountingOperationUpload,
)
from caerp.models.accounting.treasury_measures import (
    TreasuryMeasureGrid,
    TreasuryMeasureType,
    TreasuryMeasureTypeCategory,
)
from caerp.models.accounting.income_statement_measures import (
    IncomeStatementMeasureType,
    IncomeStatementMeasureTypeCategory,
    IncomeStatementMeasureGrid,
)
from caerp.models.accounting.balance_sheet_measures import (
    BalanceSheetMeasureGrid,
    ActiveBalanceSheetMeasureType,
    PassiveBalanceSheetMeasureType,
)

from caerp.models.accounting.accounting_closures import (
    AccountingClosure,
)
from caerp.models.accounting.general_ledger_account_wordings import (
    GeneralLedgerAccountWording,
)
from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule
from caerp.models.form_options import FormFieldDefinition
from caerp.models.export.accounting_export_log import (
    AccountingExportLogEntry,
)
from caerp.compute import math_utils
from caerp.models.notification import Notification
from caerp.models.custom_documentation import CustomDocumentation

DEFAULT_PERM = [
    (
        Allow,
        "group:admin",
        ALL_PERMISSIONS,
    ),
    (Deny, "group:manager", ("admin",)),
    (
        Allow,
        "group:manager",
        ALL_PERMISSIONS,
    ),
    (
        Allow,
        "group:contractor",
        ("visit",),
    ),
    (Allow, "group:constructor", ("add.construction",)),
]
# Nouveau format de permission
# Dans l'ancien format l'admin avait un wildcard
# Mais il peut arriver que certaines actions soient également interdites aux
# admins
DEFAULT_PERM_NEW = [
    (
        Allow,
        "group:admin",
        (
            "admin",
            "manage",
            "admin_treasury",
            "admin.training",
            "admin_invoices",
            "admin.estimations",
            "admin.expensesheet",
            "admin.supplier_order",
            "admin.supplier_invoice",
            # activity
            "add.activity",
            "list.activity",
            "admin.activity",
            # workshop
            "add.workshop",
            "admin.workshop",
            "edit.workshop",
            "edit_owner.event",
            "list.workshop",
            "view.workshop",
            "view.timeslot",
            # project
            "admin.project",
        ),
    ),
    (Allow, "group:contractor", ()),
    (
        Allow,
        "group:manager",
        (
            "manage",
            "admin_treasury",
            "admin.training",
            "admin_invoices,",
            "admin.estimations",
            "admin.expensesheet",
            "admin.supplier_order",
            "admin.supplier_invoice",
            # activity
            "add.activity",
            "list.activity",
            # workshop
            "add.workshop",
            "admin.workshop",
            "edit.workshop",
            "list.workshop",
            "view.workshop",
            "view.timeslot",
        ),
    ),
    (Allow, "group:constructor", ("add.construction",)),
    (Deny, "group:estimation_only", ("add.invoice",)),
]


class RootFactory(dict):
    """
    Ressource factory, returns the appropriate resource regarding
    the request object
    """

    __name__ = "root"
    # item structure :
    # traversal_name, object_name, factory
    leaves = (
        (
            "activities",
            "activity",
            Activity,
        ),
        (
            "accounting_operation_uploads",
            "accounting_operation_upload",
            AccountingOperationUpload,
        ),
        (
            "companies",
            "company",
            Company,
        ),
        (
            "competences",
            "competence",
            CompetenceGrid,
        ),
        (
            "competence_items",
            "competence_item",
            CompetenceGridItem,
        ),
        (
            "competence_subitems",
            "competence_subitem",
            CompetenceGridSubItem,
        ),
        (
            "configurable_options",
            "configurable_options",
            ConfigurableOption,
        ),
        (
            "customers",
            "customer",
            Customer,
        ),
        (
            "suppliers",
            "supplier",
            Supplier,
        ),
        (
            "discount_lines",
            "discount_line",
            DiscountLine,
        ),
        (
            "post_ttc_lines",
            "post_ttc_line",
            PostTTCLine,
        ),
        (
            "expenses",
            "expense",
            ExpenseSheet,
        ),
        (
            "expenselines",
            "expenseline",
            BaseExpenseLine,
        ),
        (
            "expense_types",
            "expense_type",
            ExpenseType,
        ),
        (
            "expense_payments",
            "expense_payment",
            ExpensePayment,
        ),
        (
            "form_field_definitions",
            "form_field_definition",
            FormFieldDefinition,
        ),
        ("supplier_invoices", "supplier_invoice", SupplierInvoice),
        (
            "supplier_invoicelines",
            "supplier_invoiceline",
            SupplierInvoiceLine,
        ),
        ("supplier_payments", "supplier_payment", BaseSupplierInvoicePayment),
        ("supplier_orders", "supplier_order", SupplierOrder),
        ("supplier_orderlines", "supplier_orderline", SupplierOrderLine),
        (
            "files",
            "file",
            File,
        ),
        ("nodes", "node", Node),
        (
            "statuslogentries",
            "statuslogentry",
            StatusLogEntry,
        ),
        (
            "tasks",
            "task",
            Task,
        ),
        (
            "income_statement_measure_grids",
            "income_statement_measure_grid",
            IncomeStatementMeasureGrid,
        ),
        (
            "income_statement_measure_types",
            "income_statement_measure_type",
            IncomeStatementMeasureType,
        ),
        (
            "income_statement_measure_type_categories",
            "income_statement_measure_type_category",
            IncomeStatementMeasureTypeCategory,
        ),
        (
            "closure_list",
            "closures_list",
            AccountingClosure,
        ),
        (
            "general_ledger_account_wordings_list",
            "general_ledger_account_wording_list",
            GeneralLedgerAccountWording,
        ),
        (
            "custom_invoice_book_entry_modules",
            "custom_invoice_book_entry_module",
            CustomInvoiceBookEntryModule,
        ),
        (
            "indicators",
            "indicator",
            Indicator,
        ),
        (
            "jobs",
            "job",
            Job,
        ),
        (
            "logins",
            "login",
            Login,
        ),
        (
            "base_task_payments",
            "base_task_payment",
            BaseTaskPayment,
        ),
        (
            "payments",
            "payment",
            Payment,
        ),
        (
            "payment_lines",
            "payment_line",
            PaymentLine,
        ),
        (
            "phases",
            "phase",
            Phase,
        ),
        (
            "projects",
            "project",
            Project,
        ),
        ("project_types", "project_type", ProjectType),
        # Catalogue produit
        (
            "base_sale_products",
            "base_sale_product",
            BaseSaleProduct,
        ),
        (
            "sale_categories",
            "sale_category",
            SaleProductCategory,
        ),
        (
            "work_items",
            "work_item",
            WorkItem,
        ),
        (
            "stock_operations",
            "stock_operation",
            SaleProductStockOperation,
        ),
        # étude de prix
        ("price_studies", "price_study", PriceStudy),
        (
            "price_study_chapters",
            "price_study_chapter",
            PriceStudyChapter,
        ),
        (
            "base_price_study_products",
            "base_price_study_product",
            BasePriceStudyProduct,
        ),
        (
            "price_study_discounts",
            "price_study_discount",
            PriceStudyDiscount,
        ),
        (
            "price_study_work_items",
            "price_study_work_item",
            PriceStudyWorkItem,
        ),
        # Avancement
        ("progress_invoicing_plans", "progress_invoicing_plan", ProgressInvoicingPlan),
        (
            "progress_invoicing_chapters",
            "progress_invoicing_chapter",
            ProgressInvoicingChapter,
        ),
        (
            "progress_invoicing_base_products",
            "progress_invoicing_base_product",
            ProgressInvoicingBaseProduct,
        ),
        (
            "progress_invoicing_work_items",
            "progress_invoicing_work_item",
            ProgressInvoicingWorkItem,
        ),
        # Statistiques
        (
            "statistics",
            "statistic",
            StatisticSheet,
        ),
        (
            "statistic_entries",
            "statistic_entry",
            StatisticEntry,
        ),
        (
            "statistic_criteria",
            "statistic_criterion",
            StatisticCriterion,
        ),
        # Notifications
        ("notifications", "notification", Notification),
        ("businesses", "business", Business),
        ("business_types", "business_type", BusinessType),
        ("tasks", "task", Task),
        ("task_lines", "task_line", TaskLine),
        ("task_line_groups", "task_line_group", TaskLineGroup),
        ("task_mentions", "task_mention", TaskMention),
        ("task_insurance_options", "task_insurance_option", TaskInsuranceOption),
        (
            "templates",
            "template",
            Template,
        ),
        (
            "templatinghistory",
            "templatinghistory",
            TemplatingHistory,
        ),
        (
            "balance_sheet_measure_grids",
            "balance_sheet__measure_grid",
            BalanceSheetMeasureGrid,
        ),
        (
            "active_balance_sheet_measure_types",
            "active_balance_sheet_measure_type",
            ActiveBalanceSheetMeasureType,
        ),
        (
            "passive_balance_sheet_measure_types",
            "passive_balance_sheet_measure_type",
            PassiveBalanceSheetMeasureType,
        ),
        (
            "treasury_measure_grids",
            "treasury_measure_grid",
            TreasuryMeasureGrid,
        ),
        (
            "treasury_measure_types",
            "treasury_measure_type",
            TreasuryMeasureType,
        ),
        (
            "treasury_measure_type_categories",
            "treasury_measure_type_category",
            TreasuryMeasureTypeCategory,
        ),
        (
            "timeslots",
            "timeslot",
            Timeslot,
        ),
        (
            "trainerdatas",
            "trainerdata",
            TrainerDatas,
        ),
        (
            "tvas",
            "tva",
            Tva,
        ),
        (
            "users",
            "user",
            User,
        ),
        (
            "userdatas",
            "userdatas",
            UserDatas,
        ),
        (
            "workshops",
            "workshop",
            Workshop,
        ),
        (
            "career_stages",
            "career_stage",
            CareerStage,
        ),
        (
            "career_path",
            "career_path",
            CareerPath,
        ),
        (
            "bank_remittances",
            "bank_remittance",
            BankRemittance,
        ),
        (
            "custom_documentations",
            "custom_documentation",
            CustomDocumentation,
        ),
    )
    subtrees = ()

    def __acl__(self):
        """
        Default permissions
        """
        acl = DEFAULT_PERM[:]
        acl.append(
            (
                Allow,
                Authenticated,
                "view",
            )
        )
        return acl

    def __init__(self, request):
        self.request = request

        logger = logging.getLogger(__name__)

        for traversal_name, object_name, factory in self.leaves:
            self[traversal_name] = TraversalDbAccess(
                self,
                traversal_name,
                object_name,
                factory,
                logger,
                request,
            )

        for traversal_name, subtree in self.subtrees:
            self[traversal_name] = subtree

        self["configfiles"] = TraversalDbAccess(
            self,
            "configfiles",
            "config_file",
            ConfigFiles,
            logger,
            request,
            id_key="key",
            public=True,
        )

    @classmethod
    def register_subtree(cls, traversal_name, subtree):
        cls.subtrees = cls.subtrees + ((traversal_name, subtree),)


class TraversalNode(dict):
    """
    Class representing a simple traversal node
    """

    def __acl__(self):
        """
        Default permissions
        """
        acl = DEFAULT_PERM[:]
        return acl


class TraversalDbAccess:
    """
    Class handling access to dbrelated objects
    """

    __acl__ = DEFAULT_PERM[:]
    dbsession = None

    def __init__(
        self,
        parent,
        traversal_name,
        object_name,
        factory,
        logger,
        request,
        id_key="id",
        public=False,
    ):
        self.__parent__ = parent
        self.factory = factory
        self.object_name = object_name
        self.__name__ = traversal_name
        self.id_key = id_key
        self.logger = logger
        self.public = public
        self.request = request

    def __getitem__(self, key):
        if not self.request.authenticated_userid and not self.public:
            from pyramid.httpexceptions import HTTPForbidden

            self.logger.error("HTTP Forbidden view the user is not connected")
            raise HTTPForbidden()
        self.logger.debug("Retrieving the context of type : {}".format(self.__name__))
        self.logger.debug("With ID : {}".format(key))
        return self._get_item(self.factory, key, self.object_name)

    def _get_item(self, klass, key, object_name):
        assert self.dbsession is not None, "Missing dbsession"

        dbsession = self.dbsession()
        obj = (
            dbsession.query(klass)
            .options(undefer_group("edit"))
            .filter(getattr(klass, self.id_key) == key)
            .scalar()
        )

        if obj is None:
            self.logger.debug("No object found")
            raise KeyError

        obj.__name__ = object_name
        # NB : Log Important qui force le chargement de la "vraie" classe de
        # l'objet pour le cas du polymorphisme, si l'objet est un Invoice, et
        # que le traversal récupère un Task, il sera automatiquement casté
        # comme une Invoice par le log ci-dessous
        self.logger.debug(obj)
        return obj


def get_current_login():
    request = get_current_request()
    user = request.identity
    result = None
    if user is not None:
        result = user.login
    return result


def get_base_acl(self):
    """
    return the base acl
    """
    acl = DEFAULT_PERM[:]
    acl.append(
        (
            Allow,
            Authenticated,
            "view",
        )
    )
    return acl


def get_event_acl(self):
    """
    Compute acl for the Event base class
    """
    acl = []
    # Prior to default ACL because we want to forbid self-signin on closed
    # workshops even for admins.
    if self.signup_mode == "open":
        acl.append((Allow, Authenticated, ("signup.event", "signout.event")))
    else:
        acl.append((Deny, Everyone, ("signup.event", "signout.event")))

    acl += DEFAULT_PERM_NEW[:]

    participants_perms = (
        "view.activity",
        "view.file",
    )
    acl.extend(
        (Allow, user.login.login, participants_perms) for user in self.participants
    )
    return acl


def get_activity_acl(self):
    """
    Return acl for activities : companies can also view
    """
    acl = get_event_acl(self)

    admin_perms = (
        "view.activity",
        "view.file",
        "edit.file",
        "delete.file",
        "edit.activity",
        "admin.activity",
    )

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))

    for company in self.companies:
        acl.append(
            (
                Allow,
                "company:{}".format(company.id),
                ("view.activity", "view.file"),
            )
        )
    return acl


def get_workshop_acl(self):
    """
    Return ACL for workshops
    """
    acl = get_event_acl(self)

    admin_perms = (
        "view.file",
        "edit.file",
        "delete.file",
    )

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))

    trainers_perms = (
        "add.workshop",
        "edit.workshop",
        "view.workshop",
        "view.file",
        "edit.file",
    )

    participants_perms = ("view.workshop",)

    acl.extend(
        (Allow, user.login.login, participants_perms) for user in self.participants
    )
    acl.extend((Allow, user.login.login, trainers_perms) for user in self.trainers)

    if self.company_manager is not None:
        for employee in self.company_manager.employees:
            if employee.login:
                if "trainer" in employee.login.groups:
                    acl.append((Allow, employee.login.login, trainers_perms))

    if self.signup_mode == "open":
        acl.append((Allow, Authenticated, "view.workshop"))

    return acl


def get_timeslot_acl(self):
    """
    Return ACL for timeslots
    """
    acl = get_event_acl(self)
    if self.workshop:
        if self.workshop.company_manager is not None:
            for employee in self.workshop.company_manager.employees:
                if "trainer" in employee.login.groups:
                    acl.append((Allow, employee.login.login, "view.timeslot"))
        for trainer in self.workshop.trainers:
            if trainer.login:
                acl.append(
                    (
                        Allow,
                        trainer.login.login,
                        "view.timeslot",
                    )
                )
    return acl


def get_company_acl(self):
    """
    Compute the company's acl
    """
    acl = DEFAULT_PERM_NEW[:]
    acl.append((Allow, Authenticated, "visit"))
    perms = [
        "view.company",
        "edit_company",
        # for logo and header
        "view.file",
        "list_customers",
        "add_customer",
        "list_suppliers",
        "add_supplier",
        "list_projects",
        "add_project",
        "add.project",
        "list_estimations",
        "list_invoices",
        "edit_commercial_handling",
        "list_expenses",
        "add.expense",
        "add.expensesheet",
        "list.sale_products",
        "add.sale_product",
        "list.sale_product_categories",
        "add.sale_product_category",
        "list_treasury_files",
        # Accompagnement
        "list.activity",
        "list.workshop",
        # New format
        "view.accounting",
        "list.estimation",
        "list.invoice",
        "view.commercial",
        "view.treasury",
        # Supplier Orders
        "add.supplier_order",
        "list.supplier_order",
        "list.supplier_invoice",
        "add.supplier_invoice",
        # Invoice
        "add.invoice",
        # Estimation
        "add.estimation",
        # Business
        "list.business",
    ]

    for group_name, perm_suffix in (
        ("trainer", "training"),
        ("constructor", "construction"),
    ):
        if self.has_group_member(group_name):
            perms.append("add.%s" % perm_suffix)
            perms.append("list.%s" % perm_suffix)

    # Copy the perms
    admin_perms = perms[:]
    admin_perms.append("admin_company")

    acl.append((Allow, "company:{}".format(self.id), perms))
    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def _get_admin_user_base_acl(self):
    """
    Build acl for user account management for admins

    :returns: A list of user acls
    """
    perms = (
        "view.user",
        "edit.user",
        "admin.user",
        "delete.user",
        "add.holiday",
        "list.holidays",
        "list.company",
        "admin.company",
        "add.activity",
        "list.activity",
        "add.workshop",
        "list.workshop",
        "add.userdatas",
        "add.login",
        "add.trainerdatas",
        # for photos
        "view.file",
    )
    for group in Group.query().options(load_only("name")).filter(Group.name != "admin"):
        perms += ("addgroup.%s" % group.name,)

    admin_perms = perms + ("addgroup.admin",)

    return [
        (Allow, "group:admin", admin_perms),
        (Allow, "group:manager", perms),
    ]


def _get_user_base_acl(self):
    """
    Build acl for user account management for the owner

    :returns: The list of user acls
    """
    result = []
    if self.login and self.login.active:
        perms = (
            "view.user",
            "set_email.user",
            "list.holidays",
            "add.holiday",
            "edit.holiday",
            "list_competences",
            # for photos
            "view.file",
        )
        result = [(Allow, self.login.login, perms)]
    return result


def _get_admin_login_base_acl(user):
    """
    Build acl for login management for admins

    :params obj user: A User instance
    :returns: A list of user acls (in the format expected by Pyramid)
    """
    perms = (
        "view.login",
        "edit.login",
        "admin.login",
        "set_password.login",
        "delete.login",
        "disable.login",
    )
    return [
        (Allow, "group:admin", perms),
        (Allow, "group:manager", perms),
    ]


def _get_login_base_acl(user):
    """
    Build acl for login management for admins

    :params obj user: A User instance
    :returns: A list of user acls (in the format expected by Pyramid)
    """
    if user.login and user.login.active:
        perms = ("view.login", "set_password.login")
        return [(Allow, user.login.login, perms)]
    return []


def _get_admin_userdatas_base_acl(self):
    """
    Build acl for userdatas management for admins
    """
    perms = (
        "view.userdatas",
        "edit.userdatas",
        "admin.userdatas",
        "delete.userdatas",
        "addfile.userdatas",
        "filelist.userdatas",
        "py3o.userdatas",
        "history.userdatas",
        "doctypes.userdatas",
        "view.file",
        "edit.file",
        "delete.file",
    )

    return [
        (Allow, "group:admin", perms),
        (Allow, "group:manager", perms),
    ]


def _get_userdatas_base_acl(user):
    """
    Build acl for userdatas management for users

    :params obj user: A User instance
    :returns: A list of user acls (in the format expected by Pyramid)
    """
    result = []
    if user.login and user.login.active:
        perms = (
            "filelist.userdatas",
            "view.file",
        )

        result = [
            (Allow, user.login.login, perms),
        ]
    return result


def _get_admin_trainerdatas_base_acl(user):
    """
    Collect trainer datas management acl for admins

    :params obj user: A User instance
    :returns: A list of user acls (in the format expected by Pyramid)
    """
    perms = (
        "view.trainerdatas",
        "edit.trainerdatas",
        "delete.trainerdatas",
        "disable.trainerdatas",
        "admin.trainerdatas",
        "addfile.trainerdatas",
        "filelist.trainerdatas",
        "view.file",
        "edit.file",
        "delete.file",
    )
    return [
        (Allow, "group:admin", perms),
        (Allow, "group:manager", perms),
    ]


def _get_trainerdatas_base_acl(user):
    """
    Collect trainer datas management acl for owner

    :params obj user: A User instance
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    result = []
    if user.login and user.login.active:
        perms = (
            "view.trainerdatas",
            "edit.trainerdatas",
            "view.file",
        )

        result = [
            (Allow, user.login.login, perms),
        ]
    return result


def get_user_acl(self):
    """
    Collect acl for a user context
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    if self.id <= 0:
        return (Deny, Everyone, ALL_PERMISSIONS)

    acl = DEFAULT_PERM_NEW[:]

    acl.extend(_get_admin_user_base_acl(self))
    acl.extend(_get_admin_login_base_acl(self))
    acl.extend(_get_admin_userdatas_base_acl(self))
    acl.extend(_get_admin_trainerdatas_base_acl(self))
    acl.extend(_get_user_base_acl(self))
    acl.extend(_get_login_base_acl(self))
    acl.extend(_get_userdatas_base_acl(self))
    acl.extend(_get_trainerdatas_base_acl(self))
    return acl


def get_userdatas_acl(self):
    """
    Collect acl for a UserDatas context
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    acl = DEFAULT_PERM_NEW[:]
    if self.user is not None:
        acl.extend(_get_admin_userdatas_base_acl(self.user))
        acl.extend(_get_userdatas_base_acl(self.user))
    return acl


def get_career_path_acl(self):
    """
    Collect acl for a CareerPath context
    :returns: A list of user aces (in the format expected by Pyramid)
    """
    acl = get_userdatas_acl(self.userdatas)
    if self.userdatas.user is not None:
        acl = get_user_acl(self.userdatas.user)
    return acl


def get_trainerdatas_acl(self):
    """
    Collect acl for TrainerDatas context

    :returns: A list of user aces (in the format expected by Pyramid)
    """
    acl = DEFAULT_PERM_NEW[:]
    if self.user is not None:
        acl.extend(_get_admin_trainerdatas_base_acl(self.user))
        acl.extend(_get_trainerdatas_base_acl(self.user))
    return acl


def get_login_acl(self):
    """
    Compute acl for a login object

    :returns: A list of aces (in the format expected by Pyramid)
    """
    acl = DEFAULT_PERM_NEW[:]
    if self.user is not None:
        acl.extend(_get_admin_login_base_acl(self.user))
        acl.extend(_get_login_base_acl(self.user))
    return acl


# invoice/estimation/cancelinvoice/supplier_order/supplier_invoice
def _get_user_status_acl(self, type_, include_duplicate=True):
    """
    Return the common status related acls
    """
    acl = []

    perms = (
        "view.node",
        "view.%s" % type_,
        "view.file",
        "add.file",
        "edit.file",
        "delete.file",
        "list.files",
    )
    if include_duplicate:
        perms += ("duplicate.%s" % type_,)

    # Some classes holds their validation status un `validation_status` other
    # in `status`
    try:
        validation_status = self.validation_status
    except AttributeError:
        validation_status = self.status

    if validation_status in ("draft", "invalid"):
        perms += (
            "edit.%s" % type_,
            "wait.%s" % type_,
            "delete.%s" % type_,
            "draft.%s" % type_,
        )
    if validation_status in ("wait",):
        perms += ("draft.%s" % type_,)

    acl.append((Allow, "company:{}".format(self.company_id), perms))
    return acl


def _get_admin_status_acl(self, type_, include_duplicate=True):
    """
    Return the common status related acls
    """
    perms = (
        "view.node",
        "view.%s" % type_,
        "admin.%s" % type_,
        "view.file",
        "add.file",
        "edit.file",
        "delete.file",
        "list.files",
    )
    if include_duplicate:
        perms += ("duplicate.%s" % type_,)
    try:
        validation_status = self.validation_status
    except AttributeError:
        validation_status = self.status

    if validation_status in ("draft", "wait", "invalid"):
        perms += (
            "edit.%s" % type_,
            "valid.%s" % type_,
            "delete.%s" % type_,
            "draft.%s" % type_,
        )
        if validation_status == "wait":
            perms += ("invalid.%s" % type_,)
        else:
            perms += ("wait.%s" % type_,)

    return [
        (Allow, "group:admin", perms),
        (Allow, "group:manager", perms),
    ]


def get_estimation_default_acl(self):
    """
    Return acl for the estimation handling

    :returns: A pyramid acl list
    :rtype: list
    """
    acl = DEFAULT_PERM_NEW[:]

    acl.extend(_get_admin_status_acl(self, "estimation"))
    admin_perms = ("duplicate.estimation",)

    if self.status == "valid":
        admin_perms += ("set_signed_status.estimation",)

        if self.internal:
            if not self.supplier_order_id:
                # Laisse le temps à celery de générer la commande fournisseur interne
                now = datetime.datetime.now()
                if self.status_date < now - datetime.timedelta(minutes=1):
                    admin_perms += ("gen_supplier_order.estimation",)
            # Fix #3897 : on permet au client signer le devis
            if self.signed_status != "signed":
                acl.append(
                    (
                        Allow,
                        "company:{}".format(self.customer.source_company_id),
                        "set_signed_status.estimation",
                    )
                )

        if self.signed_status != "signed" and not self.geninv:
            admin_perms += ("set_date.estimation",)

        if self.signed_status != "aborted":
            if self.project.project_type.with_business:
                admin_perms += ("genbusiness.estimation",)
            else:
                admin_perms += ("geninv.estimation",)

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    # Common estimation access acl
    # Auto validation avec et sans montant limite
    if self.status != "valid":
        login = get_current_login()
        if login:
            estimation_limit_amount = login.estimation_limit_amount
            total = math_utils.integer_to_amount(self.total_ht(), 5)
            acl.append((Allow, "group:estimation_validation", "edit.estimation"))
            if estimation_limit_amount is None or total <= estimation_limit_amount:
                acl.append((Allow, "group:estimation_validation", "valid.estimation"))

    acl.extend(_get_user_status_acl(self, "estimation"))

    perms = ("duplicate.estimation",)

    if self.status == "valid":
        perms += ("set_signed_status.estimation",)
        if not self.signed_status == "aborted":
            if self.project.project_type.with_business:
                perms += ("genbusiness.estimation",)
            else:
                perms += ("geninv.estimation",)

    if perms:
        acl.append((Allow, "company:{}".format(self.company_id), perms))
    return acl


def get_invoice_default_acl(self):
    """
    Return the acl for invoices

    :returns: A pyramid acl list
    :rtype: list
    """
    acl = DEFAULT_PERM_NEW[:]
    can_receive_payment = False
    if self.invoicing_mode == self.PROGRESS_MODE:
        acl.append((Deny, Everyone, "duplicate.invoice"))

    acl.extend(_get_admin_status_acl(self, "invoice"))

    admin_perms = ()
    if self.invoicing_mode == self.CLASSIC_MODE:
        admin_perms += ("duplicate.invoice",)

    if self.status == "valid":
        if self.paid_status != "resulted":
            admin_perms += ("add_payment.invoice",)
            if self.total() > 0:
                admin_perms += ("gencinv.invoice",)
        elif self.total() > 0 and not self.internal:
            # Ici on autorise la génération d'avoir pour des factures encaissées
            # mais pas dans le cas des factures internes
            admin_perms += ("gencinv.invoice",)

        if self.paid_status == "waiting":
            admin_perms += ("set_date.invoice",)

        if self.internal and not self.supplier_invoice_id:
            # Laisse le temps à celery de générer la facture fournisseur interne
            now = datetime.datetime.now()
            if self.status_date < now - datetime.timedelta(minutes=1):
                admin_perms += ("gen_supplier_invoice.invoice",)

    admin_perms += ("set_treasury.invoice",)

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    # Auto validation avec et sans montant limite
    if self.status != "valid":
        login = get_current_login()
        if login is not None:
            invoice_limit_amount = login.invoice_limit_amount
            total = math_utils.integer_to_amount(self.total_ht(), 5)
            acl.append((Allow, "group:invoice_validation", "edit.invoice"))
            if invoice_limit_amount is None or total <= invoice_limit_amount:
                acl.append((Allow, "group:invoice_validation", "valid.invoice"))

    acl.append((Deny, "group:estimation_only", ("duplicate.invoice",)))
    acl.extend(_get_user_status_acl(self, "invoice"))

    perms = ()
    if self.invoicing_mode == self.CLASSIC_MODE:
        perms += ("duplicate.invoice",)

    if self.status == "valid" and self.paid_status != "resulted" and self.total() > 0:
        if not self.internal:
            acl.append((Allow, "group:payment_admin", ("add_payment.invoice",)))
        can_receive_payment = True
        perms += ("gencinv.invoice",)

    if perms:
        acl.append((Allow, "company:{}".format(self.company_id), perms))

    return acl + _get_invoice_urssaf3p_acl(self, can_receive_payment)


def _get_invoice_urssaf3p_acl(self: "Invoice", can_receive_payment):
    acl = []
    if (
        can_receive_payment
        and self.customer.urssaf_data
        and self.customer.urssaf_data.registration_status
        and self.customer.urssaf_data.registration_status.status == "valid"
        # no support of partial payment
        and self.total() == self.topay()
        # cannot request more than once
        and self.urssaf_payment_request is None
    ):
        perms = ["request_urssaf3p.invoice"]
        acl = [
            (Allow, "group:admin", perms),
            (Allow, "group:manager", perms),
            (Allow, "group:payment_admin", perms),
            (Allow, f"company:{self.company_id}", perms),
        ]
    return acl


def get_cancelinvoice_default_acl(self):
    """
    Return the acl for cancelinvoices
    """
    acl = DEFAULT_PERM_NEW[:]
    acl.extend(_get_admin_status_acl(self, "cancelinvoice", include_duplicate=False))

    admin_perms = ()
    if self.status == "valid":
        admin_perms += ("set_treasury.cancelinvoice", "set_date.cancelinvoice")
        if self.internal and not self.supplier_invoice_id:
            # Laisse le temps à celery de générer la facture fournisseur interne
            now = datetime.datetime.now()
            if self.status_date < now - datetime.timedelta(minutes=1):
                admin_perms += ("gen_supplier_invoice.invoice",)

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    if self.status != "valid":
        acl.append((Allow, "group:cancelinvoice_validation", ("valid.cancelinvoice",)))

    acl.extend(_get_user_status_acl(self, "cancelinvoice", include_duplicate=False))
    return acl


def get_statuslogentry_acl(self):
    acl = DEFAULT_PERM_NEW[:]
    base_perms = [
        "view.statuslogentry",
    ]
    # Entries triggered by status change are autogenerated and cannot be edited.
    if self.status == "":
        owner_perms = [
            "edit.statuslogentry",
            "delete.statuslogentry",
        ]
    else:
        owner_perms = []

    company_id = FindCompanyService.find_company_id_from_node(self.node)
    if self.user and self.user.login:
        acl.append([Allow, self.user.login.login, base_perms + owner_perms])
    acl.append([Allow, "group:admin", base_perms + owner_perms])

    if self.visibility == "public":
        acl.append([Allow, f"company:{company_id}", base_perms])

    if self.visibility != "private":
        acl.append([Allow, "group:manager", base_perms])
    return acl


def get_task_line_group_acl(self):
    """
    Return the task line acl
    """
    return self.task.__acl__()


def get_task_line_acl(self):
    """
    Return the task line acl
    """
    return self.group.__acl__()


def get_discount_line_acl(self):
    """
    Return the acls for accessing the discount line
    """
    return self.task.__acl__()


def get_post_ttc_line_acl(self):
    """
    Return the acls for accessing the post-TTC line
    """
    return self.task.__acl__()


def get_payment_line_acl(self):
    """
    Return the acls for accessing a payment line
    """
    return self.task.__acl__()


def get_expense_sheet_default_acl(self):
    """
    Compute the expense Sheet acl

    view
    edit
    add_payment

    wait
    valid
    invalid
    delete

    add.file
    edit.file
    view.file

    :returns: Pyramid acl
    :rtype: list
    """
    acl = DEFAULT_PERM_NEW[:]
    acl.extend(_get_admin_status_acl(self, "expensesheet"))

    admin_perms = ()
    admin_perms += ("set_treasury.expensesheet",)

    if self.status == "valid" and self.paid_status != "resulted":
        admin_perms += ("add_payment.expensesheet",)

    admin_perms += ("set_justified.expensesheet",)

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    acl.extend(_get_user_status_acl(self, "expensesheet"))

    return acl


def get_expenseline_acl(self):
    """
    Return the default acl for an expenseline
    """
    return get_expense_sheet_default_acl(self.sheet)


def get_supplier_order_default_acl(self):
    """
    view
    edit

    wait
    valid
    invalid
    delete

    add.file
    edit.file
    view.file

    :returns: Pyramid acl
    :rtype: list
    """
    acl = DEFAULT_PERM_NEW[:]

    if self.internal:
        acl.append((Deny, Everyone, ("duplicate.supplier_order",)))
        acl.append((Deny, Everyone, ("edit.supplier_order",)))
        acl.append((Deny, Everyone, ("edit.file",)))

    acl.extend(_get_admin_status_acl(self, "supplier_order"))

    admin_perms = ()

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    acl.extend(_get_user_status_acl(self, "supplier_order"))

    # Allow or deny autovalidation
    if self.status in ("draft", "wait", "invalid"):
        login = get_current_login()
        if login is not None:
            supplier_order_limit_amount = login.supplier_order_limit_amount
            total = math_utils.integer_to_amount(self.total_ht)

            if (
                supplier_order_limit_amount is None
                or total <= supplier_order_limit_amount
            ):
                autovalidate = (
                    Allow,
                    "group:supplier_order_validation",
                    "valid.supplier_order",
                )
                acl.append(autovalidate)
    return acl


def get_supplier_order_line_acl(self):
    return get_supplier_order_default_acl(self.supplier_order)


def get_supplier_invoice_acl(self):
    """
    view
    edit
    add_payment

    wait
    valid
    invalid
    delete

    add.file
    edit.file
    view.file

    :returns: Pyramid acl
    :rtype: list
    """
    acl = DEFAULT_PERM_NEW[:]
    if self.internal:
        acl.append((Deny, Everyone, "delete.supplier_invoice"))
        acl.append((Deny, Everyone, "duplicate.supplier_invoice"))
        acl.append((Deny, Everyone, "add_payment.supplier_invoice"))
    acl.extend(_get_admin_status_acl(self, "supplier_invoice"))

    admin_perms = ()

    if self.status == "valid":
        if self.paid_status != "resulted":
            admin_perms += ("add_payment.supplier_invoice",)
        if not self.exported:
            admin_perms += ("set_types.supplier_invoice",)

    if admin_perms:
        acl.append((Allow, "group:admin", admin_perms))
        acl.append((Allow, "group:manager", admin_perms))

    acl.extend(_get_user_status_acl(self, "supplier_invoice"))

    # Allow or deny autovalidation
    if self.status in ("draft", "wait", "invalid"):
        login = get_current_login()
        if login is not None:
            supplier_invoice_limit_amount = login.supplier_invoice_limit_amount
            total = math_utils.integer_to_amount(self.total_ht)

            if (
                supplier_invoice_limit_amount is None
                or total <= supplier_invoice_limit_amount
            ):
                autovalidate = (
                    Allow,
                    "group:supplier_invoice_validation",
                    "valid.supplier_invoice",
                )
                acl.append(autovalidate)
    return acl


def get_supplier_invoice_line_acl(self):
    return get_supplier_invoice_acl(self.supplier_invoice)


def _get_base_payment_acl(self, payment_admin_group):
    """
    Compute the acl for a model implementing PaymentModelMixin

    view
    edit
    delete
    """
    acl = DEFAULT_PERM_NEW[:]

    admin_perms = ("view.payment",)
    admin_perms += (
        "edit.payment",
        "delete.payment",
    )
    if self.amount > 0:
        admin_perms += ("gen_inverse.payment",)

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    if payment_admin_group:
        # On ne veut pas qu'un entrepreneur modifie un paiement exporté en compta
        if not self.exported:
            acl.append((Allow, "group:payment_admin", admin_perms))

    acl.append((Allow, "company:{}".format(self.parent.company_id), ("view.payment",)))

    return acl


def _get_sap_attestation_acl(self):
    acl = DEFAULT_PERM_NEW[:]

    admin_perms = (
        "add.file",
        "edit.file",
        "view.file",
    )
    manager_perms = admin_perms
    company_perms = ("view.file",)

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", manager_perms))
    acl.append((Allow, f"company:{self.customer.company_id}", company_perms))
    return acl


def get_task_payment_default_acl(self):
    return _get_base_payment_acl(self, payment_admin_group=True)


def get_expense_payment_acl(self):
    return _get_base_payment_acl(self, payment_admin_group=False)


def get_supplier_payment_acl(self):
    return _get_base_payment_acl(self, payment_admin_group=False)


def get_customer_acl(self):
    """
    Compute the customer's acl
    """
    acl = DEFAULT_PERM_NEW[:]
    perms = (
        "view_customer",
        "edit_customer",
        "list.estimations",
        "list.invoices",
    )

    if not self.has_tasks():
        perms += ("delete_customer",)
    else:
        acl.insert(0, (Deny, Everyone, ("delete_customer",)))

    if not self.archived:
        perms += (
            "add.estimation",
            "add.invoice",
        )
    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, "group:admin", perms))
    acl.append((Allow, "group:manager", perms))

    return acl


def get_supplier_acl(self):
    """
    Compute the supplier's acl
    """
    acl = DEFAULT_PERM[:]
    perms = (
        "view_supplier",
        "edit_supplier",
    )

    if not self.has_orders():
        perms += ("delete_supplier",)
    else:
        acl.insert(0, (Deny, Everyone, ("delete_supplier",)))

    acl.append((Allow, "company:{}".format(self.company_id), perms))

    return acl


def get_phase_acl(self):
    """
    Return acl for a phase
    """
    acl = DEFAULT_PERM[:]

    perms = ("edit.phase",)
    if DBSESSION().query(Task.id).filter_by(phase_id=self.id).count() == 0:
        perms += ("delete.phase",)
    else:
        acl.insert(0, (Deny, Everyone, ("delete.phase",)))

    company_id = FindCompanyService.find_company_id_from_node(self)
    acl.append((Allow, "company:{}".format(company_id), perms))

    return acl


def get_project_acl(self):
    """
    Return acl for a project
    """
    acl = DEFAULT_PERM_NEW[:]

    perms = (
        "view.node",
        "view_project",
        "view.project",
        "edit_project",
        "edit.project",
        "edit_phase",
        "edit.phase",
        "add_phase",
        "add.phase",
        "add.estimation",
        "add.invoice",
        "list_estimations",
        "list.estimations",
        "list_invoices",
        "list.invoices",
        "view.file",
        "list.files",
        "add.file",
        "edit.file",
        "delete.file",
    )

    if not self.has_tasks():
        perms += ("delete_project",)
    else:
        acl.insert(0, (Deny, Everyone, ("delete_project",)))

    admin_perms = perms[:]

    if self.project_type.with_business or self.project_type.include_price_study:
        perms += ("list.businesses",)

    if self.project_type.include_price_study:
        perms += (
            "list.price_studies",
            "add.price_study",
        )
        admin_perms += (
            "list.price_studies",
            "add.price_study",
        )

    admin_perms += ("list.businesses",)

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))

    acl.append((Allow, "company:{}".format(self.company_id), perms))

    return acl


def get_business_acl(self):
    """
    Compute the acl for the Business object
    """
    acl = get_project_acl(self.project)

    perms = (
        "view.business",
        "add.file",
        "py3o.business",
    )
    admin_perms = (
        "view.node",
        "view.business",
        "py3o.business",
    )

    if not self.closed:
        admin_perms += (
            "edit.business",
            "add.business_invoice",
        )
        perms += (
            "edit.business",
            "add.business_invoice",
        )

        if not self.invoices:
            perms += ("delete.business",)
            admin_perms += ("delete.business",)
        if self.file_requirement_service.get_status(self):
            admin_perms += ("close.business",)

    if self.business_type.bpf_related:
        perms += ("edit.bpf",)
        admin_perms += ("edit.bpf",)

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", perms))

    company_id = FindCompanyService.find_company_id_from_node(self)
    acl.append((Allow, "company:{}".format(company_id), perms))

    return acl


def get_file_acl(self):
    """
    Compute the acl for a file object
    a file object's acl are simply the parent's
    """
    acl = []
    if self.parent is not None:
        acl = self.parent.__acl__
    # Exceptions: headers and logos are not attached throught the Node's parent
    # rel
    elif self.company_header_backref is not None:
        acl = self.company_header_backref.__acl__
    elif self.company_logo_backref is not None:
        acl = self.company_logo_backref.__acl__
    elif self.user_photo_backref is not None:
        acl = ((Allow, Authenticated, "view.file"),)

    if acl and callable(acl):
        acl = acl()

    return acl


def get_product_category_acl(self):
    perms = (
        "view.sale_product_category",
        "edit.sale_product_category",
        "delete.sale_product_category",
    )
    acl = DEFAULT_PERM_NEW[:]
    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, "group:admin", perms))
    acl.append((Allow, "group:manager", perms))
    return acl


def get_product_acl(self):
    """ """
    acl = DEFAULT_PERM_NEW[:]

    perms = (
        "list.sale_products",
        "view.sale_product",
        "edit.sale_product",
        "list.stock_operations",
        "view.stock_operation",
        "add.stock_operation",
        "edit.stock_operation",
        "delete.stock_operation",
    )
    if not self.is_locked():
        perms += ("delete.sale_product",)

    if self.company.has_group_member("trainer"):
        perms += (
            "list.training_product",
            "add.training_product",
            "edit.training_product",
        )

    if isinstance(self, SaleProductWork):
        perms += (
            "add.work_item",
            "list.work_items",
        )

    acl.append((Allow, "company:{}".format(self.company_id), perms))
    acl.append((Allow, "group:admin", perms))
    acl.append((Allow, "group:manager", perms))
    return acl


def get_base_product_acl(self):
    acl = self.base_sale_product.__acl__
    if callable(acl):
        acl = acl()
    return acl


def get_work_item_acl(self):
    perms = (
        "list.work_items",
        "view.work_item",
        "edit.work_item",
        "delete.work_item",
    )
    acl = DEFAULT_PERM_NEW[:]
    acl.append((Allow, "company:{}".format(self.sale_product_work.company_id), perms))
    acl.append((Allow, "group:admin", perms))
    acl.append((Allow, "group:manager", perms))
    return acl


def _get_price_study_perms(study):
    perms = ("view.price_study",)

    # C'est sale ce bout de code là, on devrait traiter ce cas là autrement
    if study.is_editable():
        perms += ("edit.price_study",)

    admin_perms = perms[:]

    if study.is_admin_editable():
        admin_perms += ("edit.price_study",)

    return admin_perms, perms


def get_price_study_acl(self):
    """
    Collect PriceStudy acl
    """
    acl = DEFAULT_PERM_NEW[:]
    admin_perms, perms = _get_price_study_perms(self)

    acl.append((Allow, "company:{}".format(self.task.company_id), perms))
    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def get_price_study_product_acl(self):
    """
    Collect BasePriceStudyProduct context acl
    """
    acl = DEFAULT_PERM_NEW[:]
    admin_perms, perms = _get_price_study_perms(self.price_study)

    if isinstance(self, PriceStudyWork):
        if "edit.price_study" in perms:
            perms += ("add.work_item",)
        if "edit.price_study" in admin_perms:
            admin_perms += ("add.work_item",)

    acl.append((Allow, "company:{}".format(self.get_company_id()), perms))
    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def get_progress_invoicing_plan_perms(plan):
    perms = ("view.plan",)
    admin_perms = ("view.plan",)
    if plan.task.status != "valid":
        admin_perms += ("edit.plan",)
        if plan.task.status != "invalid":
            perms += ("edit.plan",)
    return admin_perms, perms


def get_progress_invoicing_plan_acl(self):
    acl = DEFAULT_PERM_NEW[:]
    admin_perms, perms = get_progress_invoicing_plan_perms(self)
    acl.append((Allow, "company:{}".format(self.task.company_id), perms))
    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def get_competence_acl(self):
    """
    Return acl for the Competence Grids objects
    """
    acl = DEFAULT_PERM[:]
    login = self.contractor.login.login
    acl.append((Allow, login, ("view_competence", "edit_competence")))
    return acl


def get_accounting_measure_acl(self):
    """
    Compile the default acl for TreasuryMeasureGrid and
    IncomeStatementMeasureGrid objects
    """
    acl = []
    if self.company is not None:
        acl = self.company.__acl__
        if callable(acl):
            acl = acl()
    return acl


def get_indicator_acl(self):
    """
    Compile Indicator acl
    """
    acl = DEFAULT_PERM_NEW[:]
    admin_perms = ("view.indicator",)

    if self.status == self.DANGER_STATUS:
        admin_perms += ("force.indicator",)

    else:
        admin_perms += ("valid.indicator",)

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def get_custom_business_indicator_acl(self):
    """
    Compute acl for CustomBusinessIndicator management
    """
    # Si le parent est validé et l'indicateur est ok, on ne peut plus modifier
    user_perms = ["view.indicator"]

    locked = False
    if self.status == self.SUCCESS_STATUS:
        if self.business.closed:
            locked = True

    if not locked:
        acl = get_indicator_acl(self)
        if not self.status == self.SUCCESS_STATUS:
            user_perms.append("force.indicator")

    else:
        acl = DEFAULT_PERM_NEW[:]

    company_id = FindCompanyService.find_company_id_from_node(self.business)
    if company_id:
        acl.append((Allow, "company:{}".format(company_id), user_perms))

    return acl


def get_sale_file_requirement_acl(self):
    """
    Compile acl for SaleFileRequirement instances
    """
    # Si le parent est validé et l'indicateur est ok, on ne peut plus modifier
    user_perms = ("view.indicator",)
    admin_perms = ("view.indicator",)

    locked = False
    if self.status == self.SUCCESS_STATUS and self.file_id is not None:
        if hasattr(self.node, "status") and self.node.status == "valid":
            locked = True

    if not locked:
        acl = get_indicator_acl(self)
        if self.file_id is None:
            admin_perms += ("add.file",)
            user_perms += ("add.file",)
        else:
            admin_perms += ("edit.file",)
            user_perms += ("edit.file",)

    else:
        acl = DEFAULT_PERM_NEW[:]

    company_id = FindCompanyService.find_company_id_from_node(self.node)
    if company_id:
        acl.append((Allow, "company:{}".format(company_id), user_perms))

    acl.append((Allow, "group:admin", admin_perms))
    acl.append((Allow, "group:manager", admin_perms))
    return acl


def get_notification_acl(self: Notification):
    return [
        [
            Allow,
            f"user:{self.user_id}",
            ["view.notification", "edit.notification", "delete.notification"],
        ]
    ]


def set_models_acl():
    """
    Add acl to the db objects used as context

    Here acl are set globally, but we'd like to set things more dynamically
    when different roles will be implemented
    """
    Activity.__default_acl__ = get_activity_acl
    AccountingOperationUpload.__acl__ = get_base_acl
    Business.__default_acl__ = get_business_acl
    BusinessType.__acl__ = get_base_acl
    CustomInvoiceBookEntryModule.__acl__ = get_base_acl
    CancelInvoice.__default_acl__ = get_cancelinvoice_default_acl
    Company.__acl__ = get_company_acl
    CompetenceGrid.__acl__ = get_competence_acl
    CompetenceGridItem.__acl__ = get_competence_acl
    CompetenceGridSubItem.__acl__ = get_competence_acl
    ConfigFiles.__default_acl__ = [
        (Allow, Everyone, "view"),
    ]
    ConfigurableOption.__acl__ = get_base_acl
    Customer.__default_acl__ = get_customer_acl
    Supplier.__default_acl__ = get_supplier_acl
    DiscountLine.__acl__ = get_discount_line_acl
    PostTTCLine.__acl__ = get_post_ttc_line_acl
    Estimation.__default_acl__ = get_estimation_default_acl
    ExpenseSheet.__default_acl__ = get_expense_sheet_default_acl
    ExpensePayment.__acl__ = get_expense_payment_acl
    File.__default_acl__ = get_file_acl
    FormFieldDefinition.__acl__ = get_base_acl
    InternalEstimation.__default_acl__ = get_estimation_default_acl
    InternalInvoice.__default_acl__ = get_invoice_default_acl
    InternalCancelInvoice.__default_acl__ = get_cancelinvoice_default_acl
    InternalSupplierInvoice.__acl__ = get_supplier_invoice_acl
    Invoice.__default_acl__ = get_invoice_default_acl
    Indicator.__acl__ = get_indicator_acl
    CustomBusinessIndicator.__acl__ = get_custom_business_indicator_acl
    SaleFileRequirement.__acl__ = get_sale_file_requirement_acl
    Job.__default_acl__ = DEFAULT_PERM[:]
    Login.__acl__ = get_login_acl
    Payment.__acl__ = get_task_payment_default_acl
    InternalPayment.__acl__ = get_task_payment_default_acl
    PaymentLine.__acl__ = get_payment_line_acl
    Phase.__acl__ = get_phase_acl
    Project.__default_acl__ = get_project_acl
    ProjectType.__acl__ = get_base_acl
    # Catalogue produit
    BaseSaleProduct.__acl__ = get_product_acl
    SaleProductStockOperation.__acl__ = get_base_product_acl
    SaleProductCategory.__acl__ = get_product_category_acl
    WorkItem.__acl__ = get_work_item_acl

    # étude de prix
    PriceStudy.__acl__ = get_price_study_acl
    BasePriceStudyProduct.__acl__ = get_price_study_product_acl
    PriceStudyWorkItem.__acl__ = lambda self: get_price_study_acl(
        self.price_study_work.price_study
    )
    PriceStudyDiscount.__acl__ = lambda self: get_price_study_acl(self.price_study)
    PriceStudyChapter.__acl__ = lambda self: get_price_study_acl(self.price_study)
    ProgressInvoicingPlan.__acl__ = get_progress_invoicing_plan_acl
    ProgressInvoicingChapter.__acl__ = lambda self: get_progress_invoicing_plan_acl(
        self.plan
    )
    ProgressInvoicingBaseProduct.__acl__ = lambda self: get_progress_invoicing_plan_acl(
        self.plan
    )
    ProgressInvoicingWorkItem.__acl__ = lambda self: get_progress_invoicing_plan_acl(
        self.plan
    )
    # Notifications
    Notification.__acl__ = get_notification_acl
    # stats
    StatisticSheet.__acl__ = get_base_acl
    StatisticEntry.__acl__ = get_base_acl
    StatisticCriterion.__acl__ = get_base_acl
    SupplierOrder.__acl__ = get_supplier_order_default_acl
    SupplierOrderLine.__acl__ = get_supplier_order_line_acl
    SupplierInvoice.__acl__ = get_supplier_invoice_acl
    SupplierInvoiceLine.__acl__ = get_supplier_invoice_line_acl
    SupplierInvoiceSupplierPayment.__acl__ = get_supplier_payment_acl
    SupplierInvoiceUserPayment.__acl__ = get_supplier_payment_acl
    TaskLine.__acl__ = get_task_line_acl
    TaskLineGroup.__acl__ = get_task_line_group_acl
    TaskMention.__acl__ = get_base_acl
    TaskInsuranceOption.__acl__ = get_base_acl
    Template.__default_acl__ = get_base_acl
    TemplatingHistory.__acl__ = get_base_acl
    Timeslot.__default_acl__ = get_timeslot_acl
    TrainerDatas.__default_acl__ = get_trainerdatas_acl
    BalanceSheetMeasureGrid.__acl__ = get_accounting_measure_acl
    ActiveBalanceSheetMeasureType.__acl__ = get_base_acl
    PassiveBalanceSheetMeasureType.__acl__ = get_base_acl
    TreasuryMeasureGrid.__acl__ = get_accounting_measure_acl
    TreasuryMeasureType.__acl__ = get_base_acl
    TreasuryMeasureTypeCategory.__acl__ = get_base_acl
    IncomeStatementMeasureGrid.__acl__ = get_accounting_measure_acl
    IncomeStatementMeasureType.__acl__ = get_base_acl
    IncomeStatementMeasureTypeCategory.__acl__ = get_base_acl
    AccountingClosure.__acl__ = get_base_acl
    AccountingExportLogEntry.__acl__ = get_base_acl
    GeneralLedgerAccountWording.__acl__ = get_base_acl
    User.__acl__ = get_user_acl
    UserDatas.__default_acl__ = get_userdatas_acl
    Workshop.__acl__ = get_workshop_acl

    StatusLogEntry.__acl__ = get_statuslogentry_acl

    Tva.__acl__ = get_base_acl
    BaseExpenseLine.__acl__ = get_expenseline_acl
    ExpenseType.__acl__ = get_base_acl
    CareerStage.__acl__ = get_base_acl
    CareerPath.__acl__ = get_career_path_acl
    BankRemittance.__acl__ = get_base_acl
    SAPAttestation.__acl__ = _get_sap_attestation_acl
    CustomDocumentation.__acl__ = get_base_acl
