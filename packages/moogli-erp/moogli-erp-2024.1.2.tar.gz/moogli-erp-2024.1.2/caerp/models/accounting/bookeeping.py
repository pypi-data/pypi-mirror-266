from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    Numeric,
)
from caerp_base.models.base import (
    DBBASE,
    DBSESSION,
    default_table_args,
)


class CustomInvoiceBookEntryModule(DBBASE):
    """
    An Invoice Export module configuration

    :param compte_cg_credit: The account used for 'credit'
    :param compte_cg_debit: The account used for 'debit'
    :param label_template: The label template used for this module
    :param int percentage: The percentage that should be used in this module
    """

    help_msg = """Configurez des modules de contribution personnalisés.
Ceux-ci viennent apporter de nouvelles lignes de contribution dans les \
exports des factures.
        <h4>Configuration</h4>\
        <ul> \
        <li>Un titre</li>\
        <li>Le compte général auquel la contribution est associé</li>\
        <li>Le compte de contrepartie</li>\
        <li>Un gabarit pour la génération des libellés (voir ci-dessous pour \
les variables associées)</li>\
        <li>Un taux de contribution (pourcentage prélevé sur le <b>HT</b>)\
        </li>\
        </ul>\
        <p>\
        Pour chaque module, 8 lignes seront générées (4 lignes \
analytiques et 4 lignes générales).
        Le montant du débit et du crédit seront calculés selon le pourcentage \
indiqué (taux de contribution).\
        </p>
        <h4>Variables utilisables dans les gabarits de libellés</h4>\
        <p>Il est possible de personaliser les libellés comptables à l'aide \
d'un gabarit. Plusieurs variables sont disponibles :</p>\
        <ul>\
        <li><code>{invoice.customer.label}</code> : nom du client facturé</li>\
        <li><code>{invoice.customer.code}</code> : code du client facturé</li>\
        <li><code>{company.name}</code> : nom de l'enseigne destinataire \
du paiement</li>\
        <li><code>{company.code_compta}</code> : code analytique de \
l'enseigne destinataire du paiement</li>\
        <li><code>{invoice.official_number}</code> : numéro de facture \
(pour tronquer à 9 caractères : <code>{invoice.official_number:.9}</code>)\
</li>\
        </ul>
        <p>NB : Penser à séparer les variables, par exemple par des espaces, \
sous peine de libellés peu lisibles.</p>\
        <h4>Utilisation des variables</h4>\
        ex : "Contribution {entreprise.name} {client.name} {numero_facture}"
    """
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True, info={"colanderalchemy": {"exclude": True}})
    # Le champ nom est utilisé pour faire le lien avec les contributions
    # spécifiées par enseigne
    name = Column(
        String(100),
        nullable=True,
        default=None,
        info={"colanderalchemy": {"exclude": True}},
    )
    # Le champ custom indique si un module est défini entièrement par
    # l'utilisateur ou si il a été initialisé automatiquement par de MooGLi (cas des
    # modules contribution
    # et assurance)
    custom = Column(
        Boolean(), default=True, info={"colanderalchemy": {"exclude": True}}
    )
    title = Column(
        String(100),
        info={
            "colanderalchemy": {
                "title": "Nom du module",
            }
        },
    )
    active = Column(
        Boolean(),
        default=True,
        info={
            "colanderalchemy": {
                "exclude": True,
                "title": "Is this module unactivated (deleted)",
            }
        },
    )
    enabled = Column(
        Boolean(),
        default=True,
        info={
            "colanderalchemy": {
                "title": "Activer le module ?",
                "description": (
                    "Si ce module est actif, les écritures seront produites"
                    " dans les prochains exports de facture."
                ),
            }
        },
    )
    compte_cg_credit = Column(
        String(100),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Compte de contrepartie",
                "description": "Compte utilisé pour les lignes de crédit",
            }
        },
    )
    compte_cg_debit = Column(
        String(100),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Compte de charge",
                "description": "Compte utilisé pour les lignes de débit",
            }
        },
    )
    label_template = Column(
        String(100),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Gabarit pour les libellés d'écriture",
                "description": (
                    "Les variables disponibles pour la génération des "
                    "écritures sont décrites en haut de page"
                ),
            }
        },
    )
    percentage = Column(
        Numeric(5, 2, asdecimal=False),
        nullable=False,
        info={
            "colanderalchemy": {
                "title": "Taux de contribution de ce module",
                "description": (
                    "Valeur numérique utilisée pour calculer le pourcentage du"
                    " montant HT prélevé par le biais de ce module"
                ),
            }
        },
    )

    doctype = Column(
        String(50),
        nullable=False,
        default="invoice",
        info={
            "colanderalchemy": {
                "title": "Type de document concerné",
                "description": (
                    "Pour quel type de document ces écritures "
                    "doivent-elles être générées ?"
                ),
            }
        },
    )

    @classmethod
    def get_by_name(cls, name, prefix=""):
        doctype = "{}invoice".format(prefix)
        return (
            CustomInvoiceBookEntryModule.query()
            .filter_by(name=name, doctype=doctype)
            .first()
        )

    @classmethod
    def query(cls, include_inactive=False, *args):
        q = super(CustomInvoiceBookEntryModule, cls).query(*args)
        if not include_inactive:
            q = q.filter(CustomInvoiceBookEntryModule.active == True)  # noqa:E712
        return q

    @classmethod
    def get_percentage(cls, key, prefix=""):
        doctype = "{}invoice".format(prefix)
        result = (
            DBSESSION()
            .query(cls.percentage)
            .filter(
                cls.name == key,
                cls.doctype == doctype,
            )
            .scalar()
        )
        return result
