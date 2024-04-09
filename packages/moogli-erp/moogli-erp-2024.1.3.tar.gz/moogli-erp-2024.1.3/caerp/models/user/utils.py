import json
import logging

from datetime import date
from typing import (
    Union,
    List,
)

from caerp_base.models.base import DBSESSION
from caerp.models.config import Config
from caerp.models.career_path import CareerPath
from caerp.models.user.userdatas import (
    User,
    UserDatas,
    UserDatasCustomFields,
)
from caerp.utils.colanderalchemy import get_model_columns_list


logger = logging.getLogger(__name__)


def get_userdatas_first_step(
    userdatas_id: int, limit_date: date = None, stage_type_filter: List[str] = None
) -> Union[CareerPath, None]:
    """
    Return the first CareerPath with a stage type of the user
    after the given date if specified
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param limit_date: Optional limit date, we want the first step after this date
    :param stage_type_filter: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract']

    :returns: A CareerPath (the first step) or None
    """
    first_step_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.stage_type != None)
    )
    if limit_date:
        first_step_query = first_step_query.filter(CareerPath.start_date >= limit_date)
    if stage_type_filter:
        first_step_query = first_step_query.filter(
            CareerPath.stage_type.in_(stage_type_filter)
        )
    first_step_query = first_step_query.order_by(CareerPath.start_date)
    return first_step_query.first()


def get_userdatas_last_step(
    userdatas_id: int, limit_date: date = None, stage_type_filter: List[str] = None
) -> Union[CareerPath, None]:
    """
    Return the last CareerPath with a stage type of the user
    before the given date if specified
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param limit_date: Optional limit date, we want the last step before this date
    :param stage_type_filter: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract']

    :returns: A CareerPath (the last step) or None
    """
    last_step_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.stage_type != None)
    )
    if limit_date:
        last_step_query = last_step_query.filter(CareerPath.start_date <= limit_date)
    if stage_type_filter:
        last_step_query = last_step_query.filter(
            CareerPath.stage_type.in_(stage_type_filter)
        )
    last_step_query = last_step_query.order_by(CareerPath.start_date.desc())
    return last_step_query.first()


def get_userdatas_steps_on_period(
    userdatas_id: int,
    period_start_date: date,
    period_end_date: date,
    stage_type_filter: List[str] = None,
    sort_descending: bool = False,
) -> List[CareerPath]:
    """
    Return all the CareerPath with a stage type of the user between two dates
    with the given stage types if specified

    :param userdatas_id: id of the userdatas concerned
    :param period_start_date: The period start date, we want the steps after this date
    :param period_end_date: The period end date, we want the steps before this date
    :param stage_type_filter: Optional list of the stage types we want
        eg: ['exit'], ['entry','contract','amendment']
    :param sort_descending: True if we want the steps sorted from last to first

    :returns: A list of CareerPath (the steps)
    """
    steps_query = (
        DBSESSION()
        .query(CareerPath)
        .filter(CareerPath.userdatas_id == userdatas_id)
        .filter(CareerPath.start_date >= period_start_date)
        .filter(CareerPath.start_date <= period_end_date)
        .filter(CareerPath.stage_type != None)
    )
    if stage_type_filter:
        steps_query = steps_query.filter(CareerPath.stage_type.in_(stage_type_filter))
    if sort_descending:
        steps_query = steps_query.order_by(CareerPath.start_date.desc())
    else:
        steps_query = steps_query.order_by(CareerPath.start_date)
    return steps_query.all()


def get_userdatas_entry_date(userdatas_id: int) -> Union[date, None]:
    """
    Compute the entry date of the user
    This is the start date of the first CareerPath with a stage
    of type 'entry' or 'contract'
    """
    first_entry = get_userdatas_first_step(
        userdatas_id, stage_type_filter=["entry", "contract"]
    )
    return first_entry.start_date if first_entry else None


def get_userdatas_exit_date(userdatas_id: int) -> Union[date, None]:
    """
    Compute the exit date of the user
    This is the date of the last CareerPath with a stage type if the type is 'exit'

    NB : User can exit and come back, this return the exit date only if the last
    typed step is an exit
    """
    exit_date = None
    last_step = get_userdatas_last_step(userdatas_id)
    if last_step:
        if last_step.stage_type == "exit":
            exit_date = last_step.start_date
    return exit_date


def get_userdatas_exit(userdatas_id: int) -> Union[CareerPath, None]:
    """
    Return the exit object of given user
    This is the last CareerPath with a stage type if the type is 'exit'

    NB : User can exit and come back, this return the exit only if the last
    typed step is an exit

    :returns: A CareerPath or None
    """
    last_step = get_userdatas_last_step(userdatas_id)
    if last_step:
        if last_step.stage_type == "exit":
            return last_step
    return None


def is_userdatas_active_on_period(userdatas_id: int, start: date, end: date) -> bool:
    """
    Returns whether the user was active during the given period

    This means that he has an entry before the period ends and
    no exit or an exit after the period start

    NB : User can exit and come back, the period can be on the absence
    and this function should return False in this case

    :returns: True if active else False
    """
    is_active = False
    entry_date = get_userdatas_entry_date(userdatas_id)
    if entry_date and entry_date <= end:
        exit_date = get_userdatas_exit_date(userdatas_id)
        if exit_date == None or exit_date >= start:
            is_active = True
            # Globally active, check for absences on the period
            last_step = get_userdatas_last_step(userdatas_id, start)
            if last_step:
                if last_step.stage_type == "exit":
                    period_steps = get_userdatas_steps_on_period(
                        userdatas_id,
                        start,
                        end,
                        stage_type_filter=["entry", "contract", "amendment"],
                    )
                    if not period_steps:
                        # Exit just before the period and no return during the period
                        is_active = False
    return is_active


def get_all_userdatas_active_on_period(start: date, end: date) -> List[UserDatas]:
    """
    Returns all the UserDatas active on the given period

    This means all users that has an entry before the period ends and
    no exit or an exit after the period start

    :returns: A list of UserDatas
    """
    all = (
        UserDatas.query()
        .join(CareerPath)
        .filter(CareerPath.stage_type.in_(["entry", "contract", "amendment"]))
        .all()
    )
    actives = []
    for pp in all:
        if is_userdatas_active_on_period(pp.id, start, end):
            actives.append(pp)
    logger.debug(
        f"{len(actives)} actives user on period {start.strftime('%d/%m/%Y')} \
            to {end.strftime('%d/%m/%Y')} for {len(all)} entered users"
    )
    return actives


def get_user_analytical_accounts(user_id: int) -> str:
    """
    Return a string with the analytical accounts of the given user
    """
    compta_str = ""
    user = User.get(user_id)
    for c in user.companies:
        if c.active and c.code_compta and c.code_compta not in compta_str:
            compta_str += f"{c.code_compta}, "
    if len(compta_str) > 0:
        compta_str = compta_str[:-2]
    return compta_str


def get_tuple_option_label(options_tuple: tuple, key: str) -> str:
    """
    Return label associated to a given key in a tuple of options '(key, label)'
    """
    try:
        label = [
            option_label
            for option_key, option_label in options_tuple
            if option_key == key
        ][0]
    except IndexError:
        label = ""
    return label


def get_social_statuses_label(social_statuses) -> str:
    """
    Return a string with the social statuses of the given user
    """
    if len(social_statuses) > 1:
        social_statuses_label = ""
        for social_status in social_statuses:
            social_statuses_label += f"{social_status.social_status.label} ; "
        social_statuses_label = social_statuses_label[:-3]
    elif len(social_statuses) == 1:
        social_statuses_label = social_statuses[0].social_status.label
    else:
        social_statuses_label = ""
    return social_statuses_label


def get_active_custom_fields() -> List[str]:
    """
    Returns the names of all active custom fields
    """
    return json.loads(Config.get_value("userdatas_active_custom_fields", "[]"))


def get_active_custom_fields_labels() -> List[str]:
    """
    Returns the labels of all active custom fields
    """
    active_custom_fields_labels = []
    for field in get_model_columns_list(UserDatasCustomFields):
        if field.name in get_active_custom_fields():
            active_custom_fields_labels.append(field.info["colanderalchemy"]["title"])
    return active_custom_fields_labels


def get_custom_field_value_string(userdatas: UserDatas, custom_field: str) -> str:
    """
    Return string value of the given custom field of the given userdatas

    Used for dataqueries exports
    """
    value = ""
    if userdatas.custom_fields:
        value = str(getattr(userdatas.custom_fields, custom_field))
    if value == "True":
        value = "Oui"
    return value
