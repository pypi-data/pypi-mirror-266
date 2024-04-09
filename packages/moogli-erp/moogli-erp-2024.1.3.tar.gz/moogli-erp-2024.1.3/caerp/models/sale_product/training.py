import logging
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Table,
    Text,
    Boolean,
)
from sqlalchemy.orm import (
    relationship,
)
from caerp_base.models.base import (
    DBBASE,
    default_table_args,
)
from caerp.models.options import (
    ConfigurableOption,
    get_id_foreignkey_col,
)
from .work import SaleProductWork


logger = logging.getLogger(__name__)


TRAINING_TYPE_TO_TRAINING_PRODUCT_REL_TABLE = Table(
    "training_type_sale_product_training_rel",
    DBBASE.metadata,
    Column(
        "training_type_id",
        Integer,
        ForeignKey("training_type_options.id", ondelete="cascade"),
    ),
    Column(
        "sale_product_training_id",
        Integer,
        ForeignKey(
            "sale_product_training.id",
            ondelete="cascade",
            name="fk_training_type_rel_sale_product_training_id",
        ),
    ),
    mysql_charset=default_table_args["mysql_charset"],
    mysql_engine=default_table_args["mysql_engine"],
)


class TrainingTypeOptions(ConfigurableOption):
    """
    Different type of training
    """

    __colanderalchemy_config__ = {
        "title": "Type de formation",
        "validation_msg": "Les types de formation ont bien été configurées",
    }
    id = get_id_foreignkey_col("configurable_option.id")


class SaleProductTraining(SaleProductWork):
    """
    A Training related model
    :param id: unique id
    :param goals: goals of title of the training item
    :param prerequisites: prerequisites to subscribe to the training session
    :param for_who: target of the training item
    :param duration: duration of the training item
    :param content: content of the training item
    :param teaching_method: teaching_method used in training session
    :param logistics_means: logistics_means implemented for the training session
    :param more_stuff: Les plus...
    :param evaluation: evaluation criteria
    :param place: place if the training session
    :param modality: modality of the training session
    :param types: types of the training
    :param date: date og the training session
    :param price: price of the training session
    :param free_1: free input
    :param free_2: free input
    :param free_3: free input
    :param company_id: company that owns the training
    :param company_id: company that owns the group
    """

    __tablename__ = "sale_product_training"
    __table_args__ = default_table_args
    __mapper_args__ = {"polymorphic_identity": "sale_product_training"}
    id = Column(
        ForeignKey("sale_product_work.id", ondelete="cascade"), primary_key=True
    )

    goals = Column(
        Text,
        default="",
    )

    prerequisites = Column(Text, default="")

    for_who = Column(Text, default="")

    duration = Column(Text, nullable=False, default="")

    content = Column(Text, default="")

    teaching_method = Column(Text, default="")

    logistics_means = Column(Text, default="")

    more_stuff = Column(Text, default="")

    evaluation = Column(Text, default="")

    place = Column(Text, default="")

    modality_one = Column(
        Boolean(),
        info={"colanderalchemy": {"title": "Formation intra-entreprise"}},
        default=False,
    )

    modality_two = Column(
        Boolean(),
        info=({"colanderalchemy": {"title": "Formation inter-entreprise"}}),
        default=False,
    )

    types = relationship(
        "TrainingTypeOptions",
        secondary=TRAINING_TYPE_TO_TRAINING_PRODUCT_REL_TABLE,
    )

    date = Column(Text, default="")

    price = Column(Text, default="")

    free_1 = Column(Text, default="")

    free_2 = Column(Text, default="")

    free_3 = Column(Text, default="")

    def __json__(self, request):
        """
        Json repr of our model
        """
        result = SaleProductWork.__json__(self, request)
        result.update(
            id=self.id,
            goals=self.goals,
            prerequisites=self.prerequisites,
            for_who=self.for_who,
            duration=self.duration,
            content=self.content,
            teaching_method=self.teaching_method,
            logistics_means=self.logistics_means,
            more_stuff=self.more_stuff,
            evaluation=self.evaluation,
            place=self.place,
            modality_one=self.modality_one,
            modality_two=self.modality_two,
            types=[type_.id for type_ in self.types],
            date=self.date,
            price=self.price,
            free_1=self.free_1,
            free_2=self.free_2,
            free_3=self.free_3,
        )
        return result

    def duplicate(self):
        result = SaleProductWork.duplicate(self)
        result.goals = self.goals
        result.prerequisites = self.prerequisites
        result.for_who = self.for_who
        result.duration = self.duration
        result.content = self.content
        result.teaching_method = self.teaching_method
        result.logistics_means = self.logistics_means
        result.more_stuff = self.more_stuff
        result.evaluation = self.evaluation
        result.place = self.place
        result.modality_one = self.modality_one
        result.modality_two = self.modality_two
        result.types = [type_ for type_ in self.types]
        result.date = self.date
        result.price = self.price
        result.free_1 = self.free_1
        result.free_2 = self.free_2
        result.free_3 = self.free_3
        return result
