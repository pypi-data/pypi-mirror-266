import re
from .action_items_local_constants import ACTION_ITEMS_PYTHON_PACKAGE_CODE_LOGGER_OBJECT
from logger_local.LoggerLocal import Logger
from database_mysql_local.generic_mapping import GenericMapping
from database_mysql_local.generic_crud_ml import GenericCRUDML
from user_context_remote.user_context import UserContext
from language_remote.lang_code import LangCode


DEFAULT_SCHEMA_NAME = 'action_item'
DEFAULT_ENTITY_NAME1 = 'action_item'
DEFAULT_ENTITY_NAME2 = 'contact'
DEFAULT_TABLE_NAME = 'action_item_table'
DEFAULT_ID_COLUMN_NAME = 'action_item_id'
DEFAULT_MAPPING_ID_COLUMN_NAME = 'action_item_contact_id'
DEFAULT_MAPPING_TABLE_NAME = 'action_item_contact_table'

logger = Logger.create_logger(object=ACTION_ITEMS_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)
user_context = UserContext()


class ActionItemsLocal(GenericMapping, GenericCRUDML):
    def __init__(self, default_schema_name: str = DEFAULT_SCHEMA_NAME, default_entity_name1: str = DEFAULT_ENTITY_NAME1,
                 default_entity_name2: str = DEFAULT_ENTITY_NAME2,
                 default_id_column_name: str = DEFAULT_ID_COLUMN_NAME,
                 default_table_name: str = DEFAULT_TABLE_NAME,
                 default_mapping_id_column_name: str = DEFAULT_MAPPING_TABLE_NAME,
                 default_mapping_table_name: str = DEFAULT_MAPPING_TABLE_NAME,
                 is_test_data: bool = False):

        GenericMapping.__init__(
            self, default_schema_name=default_schema_name, default_entity_name1=default_entity_name1,
            default_entity_name2=default_entity_name2, default_id_column_name=default_mapping_id_column_name,
            default_table_name=default_mapping_table_name,
            is_test_data=is_test_data
        )

        GenericCRUDML.__init__(
            self, default_schema_name=default_schema_name, default_id_column_name=default_id_column_name,
            default_table_name=default_table_name, is_test_data=is_test_data
        )

    def insert_link_action_item_contact(self, data_action_item: dict, contact_id: int,
                                        lang_code: LangCode = None,
                                        contact_dict: dict = None) -> int:
        """
        Insert link action item contact
        :param data_action_item: dict
        :param lang_code: LangCode
        :param contact_id: int
        :param contact_dict: dict
        :return: int
        """
        logger.start(object={"data_action_item": data_action_item, "lang_code": lang_code, "contact_id": contact_id,
                             "contact_dict": contact_dict})
        pattern = r'^\d+.+\d+$'
        title = data_action_item.get("title")
        ranking = None
        if re.match(pattern, title):
            priority = self.get_action_item_priority(action_item=title)
            title = title[1:-1]
            if contact_dict:
                if contact_dict.get("first_name"):
                    if contact_dict.get("last_name"):
                        contact_name = f"{contact_dict.get('first_name')} {contact_dict.get('last_name')}"
                    else:
                        contact_name = contact_dict.get("first_name")
                else:
                    if contact_dict.get("last_name"):
                        contact_name = contact_dict.get("last_name")
                    else:
                        contact_name = None
                if contact_name:
                    title = f"{title} {contact_name}"

            data_action_item["title"] = title
            ranking = self.get_rank_by_priority(priority=priority)
        lang_code = lang_code or LangCode.detect_lang_code(text=title)
        data_json = {
            "name": data_action_item.get("name"),
            "ranking": ranking,
            "profile_id1": user_context.get_effective_profile_id()
        }
        action_item_id, action_item_ml_id = self.add_value(data_ml_json=data_action_item, lang_code=lang_code, data_json=data_json)
        action_item_contact_id = self.insert_mapping(
            entity_id1=action_item_id, entity_id2=contact_id, ignore_duplicate=True,
            schema_name="action_item_contact"
        )
        insert_information = {
            "action_item_id": action_item_id,
            "action_item_ml_id": action_item_ml_id,
            "action_item_contact_id": action_item_contact_id
        }
        logger.end(object={"action_item_id": action_item_id, "action_item_ml_id": action_item_ml_id,
                           "action_item_contact_id": action_item_contact_id})
        return insert_information

    def get_action_item_priority(self, action_item: str) -> int:
        """
        Get action item priority
        :param action_item: str
        :return: int
        """
        logger.start(object={"action_item": action_item})
        if not action_item:
            return None
        priority = int(action_item[-1])
        logger.end(object={"priority": priority})
        return priority

    def get_rank_by_priority(self, priority: int) -> int:
        """
        Set rank by priority
        :param action_item: str
        :param priority: int
        :return: int
        """
        logger.start(object={"priority": priority})
        where_clause = "ranking >= %s AND ranking < %s"
        params = ((priority * 10000), ((priority + 1) * 10000))
        order_by = "ranking DESC"
        action_items_dicts = self.select_multi_dict_by_where(
            schema_name=self.schema_name,
            view_table_name="action_item_view",
            where=where_clause, params=params, order_by=order_by
        )
        if not action_items_dicts:
            ranking = priority * 10000
        else:
            ranking = action_items_dicts[0]['ranking'] + 1

        logger.end(object={"ranking": ranking})
        return ranking
