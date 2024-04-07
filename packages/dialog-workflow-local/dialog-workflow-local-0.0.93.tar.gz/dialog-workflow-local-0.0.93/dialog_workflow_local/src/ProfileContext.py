from database_mysql_local.connector import Connector
from logger_local.LoggerLocal import Logger
from variable_local.variable import VariablesLocal

from .Constants import DIALOG_WORKFLOW_CODE_LOGGER_OBJECT
from .utils import get_curr_state

logger = Logger.create_logger(object=DIALOG_WORKFLOW_CODE_LOGGER_OBJECT)


class ProfileContext(object):
    # TODO We should consider to take ProfileContact to a separate package or merge it with UserContext
    def __init__(self, profile_id):
        self.dict = {}
        self.profile_id = profile_id
        self.chosen_poll_options = {}
        self.curr_state_id = get_curr_state(self.profile_id)
        self.variables = VariablesLocal()
        self.groups = []

    def get_variable_value_by_variable_id(self, variable_id: int) -> str:
        logger.start(object={'variable_id': variable_id})
        variable_value = self.dict[variable_id]
        logger.end(object={'variable_value': variable_value})
        return variable_value

    def save_chosen_options(self, question_asked: str, variable_id: int, chosen_numbers_list: list,
                            list_of_options: list):
        """Saves the options chosen by the user in the multi_choice_poll action in a dict with the question as the key
            and a list of the options chosen as the value i.e: {<question asked> : [<chosen option 1>, <chosen option 2>, ...]}
            Also saves the chosen options in the database."""
        logger.start(object={'question_asked': question_asked, 'variable_id': variable_id,
                             'chosen_numbers_list': chosen_numbers_list, 'list_of_options': list_of_options})
        self.chosen_poll_options[question_asked] = [
            list_of_options[chosen_option - 1] for chosen_option in chosen_numbers_list]
        variable_value_to_insert = question_asked + " "
        for chosen_option in self.chosen_poll_options[question_asked]:
            variable_value_to_insert = variable_value_to_insert + \
                                       str(chosen_option) + ", "
        self.variables.set_variable_value_by_variable_id(
            variable_id, variable_value_to_insert, self.profile_id, self.curr_state_id)
        logger.end()

    def get_variable_value_by_variable_name(self, variable_name: str) -> str:
        logger.start(object={'variable_name': variable_name})
        variable_value = self.get_variable_value_by_variable_id(
            self.variables.get_variable_id_by_variable_name(variable_name))
        logger.end(object={'variable_value': variable_value})
        return variable_value

    # TODO Should be moved to variable-value-local-python-package
    def set(self, variable_id: int, variable_value: str):
        logger.start(object={'variable_id': variable_id, 'variable_value': variable_value})
        self.dict[variable_id] = variable_value
        connection = Connector.connect('logger')
        cursor = connection.cursor(dictionary=True, buffered=True)
        # cursor.execute("""USE logger""")
        # TODO Can we replace it with GenericCRUD
        cursor.execute("""INSERT INTO logger
                        (profile_id, state_id, variable_id, variable_value_new) 
                        VALUES (%s,%s,%s,%s)""",
                       (self.profile_id, self.curr_state_id, variable_id, variable_value))
        connection.commit()
        logger.end()


class ProfilesDict(object):
    def __init__(self):
        self.profiles_dict = {}

    def add(self, profile: ProfileContext):
        logger.start(object={'profile': profile})
        # TODO Should we also keep in the database?
        self.profiles_dict[profile.profile_id] = profile
        logger.end()

    def get(self, profile_id: int) -> ProfileContext or None:
        logger.start(object={'profile_id': profile_id})
        if profile_id not in self.profiles_dict:
            logger.end()
            return None
        else:
            profile_dict = self.profiles_dict[profile_id]
            logger.end(object={'profile_dict': profile_dict})
            return profile_dict
        # return None if profile_id not in self.profiles_dict else self.profiles_dict[profile_id]


class DialogWorkflowRecord(object):
    def __init__(self, record: dict) -> None:
        self.curr_state_id: int = record.get("state_id")
        self.parent_state_id: int = record.get("parent_state_id")
        self.workflow_action_id: int = record.get("workflow_action_id")
        self.lang_code = record.get("lang_code")
        self.parameter1 = record.get("parameter1")
        self.variable1_id: int = record.get("variable1_id")
        self.result_logical = record.get("result_logical")
        self.result_figure_min: float = record.get("result_figure_min")
        self.result_figure_max: float = record.get("result_figure_max")
        self.next_state_id: int = record.get("next_state_id")
        self.no_feedback_milliseconds: float = record.get("no_feedback_milliseconds")
        self.next_state_id_if_there_is_no_feedback: int = record.get("next_state_id_if_there_is_no_feedback")
