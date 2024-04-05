import json

from database_mysql_local.connector import Connector
from language_remote.lang_code import LangCode
from logger_local.LoggerLocal import Logger

from .Constants import (COMMUNICATION_TYPE, DIALOG_WORKFLOW_CODE_LOGGER_OBJECT,
                        CommunicationTypeEnum, WorkflowActionEnum)

logger = Logger.create_logger(object=DIALOG_WORKFLOW_CODE_LOGGER_OBJECT)


# from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage

# TODO: Please include type to all parameters.
# TODO: Please include return value.
# TODO: Please add short documentation per PEP8 standard

# TODO:Let's move to Object Oriented Programming

def get_variable_value_by_id(language: LangCode, variable_id: int) -> str:
    # TODO: language is not used
    logger.start(object={'variable_id': variable_id})
    connection = Connector.connect('logger')
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(
        """SELECT variable_value_new FROM logger_dialog_workflow_state_history_view WHERE variable_id= %s ORDER BY timestamp DESC""",
        (variable_id,))
    variable_value = (cursor.fetchone())["variable_value_new"]
    logger.end(object={'variable_value': variable_value})
    return variable_value


def process_message(communication_type: CommunicationTypeEnum, action_type: WorkflowActionEnum, message: str) -> str:
    """Processes message according to which communication_type is used: console or websocket
        If console then we continue the code normally.
        If websocket then we create a json out of the given message and exit(0)"""
    logger.start(object={'communication_type': communication_type, 'action_type': action_type, 'message': message})
    if communication_type == CommunicationTypeEnum.CONSOLE:
        message = message.replace('~', '\n')
    elif communication_type == CommunicationTypeEnum.WEBSOCKET:
        message = update_json_message(action_type, message)
    logger.end(object={'message': message})
    return message


def update_json_message(action_type: WorkflowActionEnum, message: str) -> json:
    """Update message to json format"""
    logger.start(object={"action_type": action_type, "message": message})
    json_message = {"message": message}
    if action_type == WorkflowActionEnum.AGE_DETECTION:
        json_message["type"] = "command"
    else:
        json_message["type"] = "text"
    json_dumps = json.dumps(json_message)
    logger.end(object={'json_dumps': json_dumps})
    return json_dumps


def update_profile_curr_state_in_db(new_state: int, profile_id):
    """This function updates the last_dialog_workflow_state_id in the profile table to the new state.
       Note that this function UPDATES the field sand doesn't INSERT into the table. """
    logger.start(object={"new_state": new_state, 'profile_id': profile_id})
    connection = Connector.connect('profile')
    cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE profile""")
    cursor.execute("""UPDATE profile_table SET last_dialog_workflow_state_id = %s WHERE (profile_id= %s)""",
                   (new_state, profile_id))
    # cursor.execute("""USE dialog_workflow""")
    connection.commit()
    logger.end()


# TODO: Make sure we have good testing coverage to this function
def store_age_detection_picture(age_range: str, profile_id: int):
    """Stores the picture in Nir's storage schema, gets a storage_id and inserts into the computer_vision_storage_table"""
    # storage = AwsS3Storage(bucket_name="storage.us-east-1.dvlp1.bubblez.life", region="us-east-1")
    # storage_id = storage.upload_file("C:\\Users\\User\\OneDrive\\Circles\\age-detection-backend\\src\\alonPicture.png", "Alon's picture", "", 1)

    # age_range_split = age_range.split('-')
    # TODO Why this is commented?
    # TODO Why we commented this? Let's uncomment
    # min_age = int(age_range_split[0][:len(age_range_split[0])-1])
    # max_age = int((age_range_split[1])[1:])
    # cursor.execute("""USE computer_vision_storage""")
    # cursor.execute("""INSERT INTO computer_vision_storage_table
    #                 (storage_id, profile_id, min_age, max_age) VALUES (%s, %s, %s, %s)""",
    #                [storage_id, profile_id, min_age, max_age])
    # connection.commit()
    pass


# TODO Shall we move it to Profile Context?
def get_curr_state(profile_id: int):
    """Returns profiles' curernt state number"""
    logger.start(object={'profile_id': profile_id})
    connection = Connector.connect('profile')
    cursor = connection.cursor(dictionary=True, buffered=True)
    # cursor.execute("""USE profile""")
    cursor.execute(
        """SELECT last_dialog_workflow_state_id FROM profile_view WHERE profile_id = %s ORDER BY profile_id DESC""",
        (profile_id,))
    curr_state = int((cursor.fetchone())["last_dialog_workflow_state_id"])
    # cursor.execute("""USE dialog_workflow""")
    logger.end(object={'curr_state': curr_state})
    return curr_state


def get_child_nodes_of_current_state(fields: list, table_name: str, values_from_where_to_select: tuple,
                                     variables_from_where_to_select: list):
    """Recieves all the relevant information and selects the child nodes of the current state from the given table, and returns them"""
    logger.start(
        object={'fields': fields, 'table_name': table_name, 'values_from_where_to_select': values_from_where_to_select,
                'variables_from_where_to_select': variables_from_where_to_select})
    sql_query = "SELECT " + ", ".join(fields) + " FROM " + table_name + " WHERE "
    # Add the variables and values to the SQL query
    for i in range(len(variables_from_where_to_select)):
        sql_query += variables_from_where_to_select[i] + " = %s"
        if i != len(variables_from_where_to_select) - 1:
            sql_query += " AND "
    connection = Connector.connect('dialog_workflow')
    cursor = connection.cursor(dictionary=True, buffered=True)
    cursor.execute(sql_query, values_from_where_to_select)
    child_nodes = cursor.fetchall()
    logger.end(object={'child_nodes': child_nodes})
    return child_nodes


class Group(object):
    def __init__(self, parameter1):
        self.parameter1 = parameter1

    # TODO Make sure we have tests for this and all other methods        
    def get_group_childs_id_bellow_parent_id(self) -> list[int]:
        """returns all the childs ids below the given parent_id.
            This function gets all the id's of records that their parent_state_id is the given id, and continues to add id's  recursively 
            until all the records that their parent_state_id matches an id in the table."""
        logger.start()
        connection = Connector.connect("group")
        cursor = connection.cursor(dictionary=True, buffered=True)
        # cursor.execute("""USE `group`""")
        # TODO Fix this SQL
        cursor.execute("""WITH RECURSIVE cte AS (
            SELECT group_view.group_id FROM group_view WHERE group_id = %s
            UNION ALL
            SELECT group_view.group_id FROM group_view 
            JOIN cte ON group_view.parent_group_id = cte.group_id
        )
        SELECT cte.group_id FROM cte""", (self.parameter1,))
        group_id_dict = cursor.fetchall()
        # TODO id -> group_id
        group_childs_id = [group['group_id'] for group in group_id_dict]
        logger.end(object={'group_childs_id': group_childs_id})
        return group_childs_id

    def get_child_group_names(self) -> list:
        """Gets all the child title names from the ml table of the given parent_id."""
        logger.start()
        group_ids = self.get_group_childs_id_bellow_parent_id()
        group_id_string = ','.join(str(group_id) for group_id in group_ids)
        connection = Connector.connect('group')
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute(f"SELECT title FROM group_ml_view WHERE group_id IN ({group_id_string}) ")
        group_name_dict = cursor.fetchall()
        child_group_names = [group['title'] for group in group_name_dict]
        logger.end(object={'child_group_names': child_group_names})
        return child_group_names

    # def get_child_group_id(self) -> list[int]:
    #     """Gets the id of all the records with the given group name"""
    #     cursor.execute("""USE `group`""")
    #     cursor.execute("""SELECT group_id from group_ml_en_view WHERE title = %s""", [self.parameter1])
    #     group_id_dict = cursor.fetchall()
    #     return [group['group_id'] for group in group_id_dict]        


# TODO Shall we move this to a menu class?
def generic_menu(options: list, got_response: bool, chosen_numbers: str, choose_one_option: bool,
                 outgoing_message: str):
    """A generic function for displaying a menu for the user.
        Returns: If not got_response: the menu options as json to send to user.
                 Otherwise, returns the chosen numbers as list in int"""
    logger.start(object={'options': options, 'got_response': got_response, 'chosen_numbers': chosen_numbers,
                         'choose_one_option': choose_one_option, 'outgoing_message': outgoing_message})
    if not got_response:
        outgoing_message += f"Please choose EXACTLY ONE option between 1-{len(options)}:~" if choose_one_option else f"Please select your desired choices, You may select any of the numbers between 1-{len(options)} with a comma seperator between each choice:~"
        outgoing_message_json = None
        for i, option in enumerate(options):
            outgoing_message = outgoing_message + f'{i + 1}) {option}~'
            outgoing_message_json = process_message(communication_type=COMMUNICATION_TYPE,
                                                    action_type=WorkflowActionEnum.TEXT_MESSAGE_ACTION,
                                                    message=outgoing_message)
        if COMMUNICATION_TYPE == CommunicationTypeEnum.WEBSOCKET:
            return outgoing_message_json

    if COMMUNICATION_TYPE == CommunicationTypeEnum.CONSOLE:
        chosen_numbers = input()
    chosen_numbers = chosen_numbers.split(',')
    generic_menu_result = [int(x) - 1 for x in chosen_numbers]
    logger.end(object={'generic_menu_result': generic_menu_result})
    return generic_menu_result
