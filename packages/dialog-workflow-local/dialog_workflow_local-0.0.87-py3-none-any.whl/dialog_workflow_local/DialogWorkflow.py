import random

from database_mysql_local.connector import Connector
from logger_local.LoggerLocal import Logger
from message_local.CompoundMessage import CompoundMessage
from user_context_remote.user_context import UserContext
from variable_local.variable import VariablesLocal

from .Constants import DIALOG_WORKFLOW_CODE_LOGGER_OBJECT
from .ProfileContext import DialogWorkflowRecord
from .action import Action
from .utils import get_curr_state, update_profile_curr_state_in_db

user = UserContext()
logger = Logger.create_logger(object=DIALOG_WORKFLOW_CODE_LOGGER_OBJECT)


# Get all potential records in a specific state and choose randomly one of them
# TODO Please use MessagesLocal to store the message(s) recieved and anwers
# TODO Please use the function defined in avatar similar to get_dialog_workflow_avatar_profile_id( profile_id1, prompt, group_id, profile_id2...) using avatar_table and avtar_group_table
def get_dialog_workflow_record(profile_curr_state: int, language: str):
    logger.start(
        object={'profile_curr_state': profile_curr_state, 'language': language})
    # TODO Change * to the fields required
    connection = Connector.connect('dialog_workflow')
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute("""SELECT * FROM dialog_workflow_state_view WHERE state_id = %s AND lang_code = %s""",
                   (profile_curr_state, language))
    optional_records = cursor.fetchall()
    if not optional_records:
        error_message = f"No records found for state_id: {profile_curr_state} and language: {language}"
        logger.error(error_message)
        logger.end()
        raise Exception(error_message)
    random_index = random.randint(0, len(optional_records) - 1)
    dialog_workflow_record = DialogWorkflowRecord(optional_records[random_index])
    logger.end(object={'dialog_workflow_record': str(dialog_workflow_record)})
    return dialog_workflow_record


def post_message(profile_id: int, incoming_message: str):
    """This function is supposed to serve as a POST request later on using REST API.
    It runs until needing input from the user, which it then sends a json to the user with the message and exits
    PARAMS: 
        1. profile_id: the profile id that sent the request
        2. incoming_message: the message he sent"""
    # TODO: remove profile_id an use user context
    logger.start(object={'profile_id': profile_id,
                         'incoming_message': incoming_message})
    # TODO Save the message using MessagesLocal (from DIALOG_WORKFLOW_PROFILE_ID, to UserContext.getEffectiveProfileId, ...)
    variables = VariablesLocal()
    profile_curr_state = get_curr_state(profile_id)
    language = user.get_effective_profile_prefered_language()
    got_response = incoming_message.strip() != ""  # This variable indicates if we must act now as we got a response from the user or as if we should send one to him
    init_action = Action(incoming_message, profile_id,
                         language, profile_curr_state, variables)
    while True:
        dialog_workflow_record = get_dialog_workflow_record(
            init_action.profile_curr_state, language)
        is_state_changed, outgoing_message = init_action.act(
            dialog_workflow_record, got_response)
        # TODO Save the message using MessagesLocal (from DIALOG_WORKFLOW_PROFILE_ID, to UserContext.getEffectiveProfileId, ...)
        if outgoing_message is not None:
            if not isinstance(outgoing_message, list):
                outgoing_compound_message = CompoundMessage(body=outgoing_message).get_message_fields()
            else:
                outgoing_compound_message = outgoing_message
            logger.end(object={'outgoing_message': str(outgoing_compound_message)})
            return outgoing_compound_message
        init_action.profile_curr_state = dialog_workflow_record.next_state_id if is_state_changed == False else init_action.profile_curr_state
        update_profile_curr_state_in_db(
            init_action.profile_curr_state, profile_id)
        got_response = False
