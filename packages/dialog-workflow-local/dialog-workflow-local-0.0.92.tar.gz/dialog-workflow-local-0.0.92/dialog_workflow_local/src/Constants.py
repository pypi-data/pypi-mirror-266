from enum import Enum

from logger_local.LoggerComponentEnum import LoggerComponentEnum
from python_sdk_remote.utilities import our_get_env


# TODO Let's use SQL2Code

# TODO Move to a seperate file
# TODO Use Sql2Code
class WorkflowActionEnum(Enum):
    PRESENT_AND_CHOOSE_SCRIPT = 0
    LABEL_ACTION = 1
    TEXT_MESSAGE_ACTION = 2
    QUESTION_ACTION = 3
    JUMP_ACTION = 4
    SEND_REST_API_ACTION = 5
    ASSIGN_VARIABLE_ACTION = 6
    INCREMENT_VARIABLE_ACTION = 7
    DECREMENT_VARIABLE_ACTION = 8
    CONDITION_ACTION = 9
    MENU_ACTION = 10
    AGE_DETECTION = 11
    MULTI_CHOICE_POLL = 12
    PRESENT_CHILD_GROUPS_NAMES_BY_ID = 13
    PRESENT_GROUPS_WITH_CERTAIN_TEXT = 14
    INSERT_MISSING_DATA = 15
    PRESENT_FORM = 16


# TODO Move to a seperate file
# TODO Use Sql2Code
# TODO Can we load it one time from database to memcache
VARIABLE_NAMES_DICT = {1: "Person Id", 2: "User Id", 3: "Profile Id", 4: "Lang Code",
                       5: "Name Prefix", 6: "First Name", 7: "Middle Name",
                       8: "Last Name", 9: "Name Suffix", 10: "Full Name",
                       11: "Country", 12: "State", 13: "County", 14: "City",
                       15: "Neighborhood", 16: "Street", 17: "House", 18: "Suite/Apartment",
                       19: "Zip Code", 20: "Post Result", 21: "Age", 22: "Result"}


class CommunicationTypeEnum(Enum):
    CONSOLE = 1
    WEBSOCKET = 2
    MESSAGE = 3


# TODO: We should align the terminology between dialog-workflow and gender-detection (INTERFACE_MODE= BATCH, INTERACTIVE)
DEFAULT_COMMUNICATION_TYPE = CommunicationTypeEnum.WEBSOCKET.value
COMMUNICATION_TYPE = CommunicationTypeEnum(int(our_get_env("COMMUNICATION_TYPE",
                                                           default=str(DEFAULT_COMMUNICATION_TYPE))))

DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_ID = 166
DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_NAME = "dialog_workflow-python-package"

DIALOG_WORKFLOW_CODE_LOGGER_OBJECT = {
    'component_id': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DIALOG_WORKFLOW_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'idan.a@circ.zone and guy.n@circ.zone'
}

LOGGER_TEST_OBJECT = DIALOG_WORKFLOW_CODE_LOGGER_OBJECT.copy()
LOGGER_TEST_OBJECT['component_category'] = LoggerComponentEnum.ComponentCategory.Unit_Test.value
