from typing import Optional, List
from zope.interface import implementer

from caerp.interfaces import IJustifiedStateManager

from caerp.models.action_manager import ActionManager, Action
from caerp.models.expense.sheet import ExpenseSheet


def _build_justified_state_manager():
    """
    Return a state manager for setting the justified status attribute on
    ExpenseSheet objects
    """
    manager = ActionManager()
    for status, icon, label, title, css in (
        (
            False,
            "clock",
            "En attente",
            "Les justificatifs n'ont pas ou pas tous été acceptés",
            "btn",
        ),
        (
            True,
            "check",
            "Acceptés",
            "Les justificatifs ont été acceptés",
            "btn",
        ),
    ):
        action = Action(
            status,
            "set_justified.expensesheet",
            status_attr="justified",
            icon=icon,
            label=label,
            title=title,
            css=css,
        )
        manager.add(action)
    return manager


@implementer(IJustifiedStateManager)
def get_default_justified_state_manager(doctype: str) -> ActionManager:
    return _build_justified_state_manager()


def set_status(request, expense_sheet: ExpenseSheet, status: str, **kw) -> ExpenseSheet:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    return manager.process(request, expense_sheet, status, **kw)


def check_allowed(
    request, expense_sheet: ExpenseSheet, status: str
) -> Optional[Action]:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    return manager.check_allowed(request, expense_sheet, status)


def get_allowed_actions(request, expense_sheet: ExpenseSheet) -> List[Action]:
    manager: ActionManager = request.find_service(
        IJustifiedStateManager, context=expense_sheet
    )
    return manager.get_allowed_actions(request, expense_sheet)
