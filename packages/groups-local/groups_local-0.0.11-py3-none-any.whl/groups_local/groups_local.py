from typing import Dict
from .groups_local_constants import GroupsLocalConstants
from database_mysql_local.generic_crud_ml import GenericCRUDML  # noqa: E402
from database_infrastructure_local.number_generator import NumberGenerator  # noqa: E402
from user_context_remote.user_context import UserContext  # noqa: E402
from logger_local.Logger import Logger  # noqa: E402
from language_remote.lang_code import LangCode  # noqa: E402

logger = Logger.create_logger(object=GroupsLocalConstants.GROUPS_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)
user_context = UserContext()

DEFAULT_SCHEMA_NAME = "group"
DEFAULT_TABLE_NAME = "group_table"
DEFAULT_VIEW_TABLE_NAME = "group_view"
DEFAULT_ID_COLUMN_NAME = "group_id"
DEFAULT_IS_MAIN_COLUMN_NAME = "is_main_title"


class GroupsLocal(GenericCRUDML):

    def __init__(self, is_test_data: bool = False):
        GenericCRUDML.__init__(self, default_schema_name=DEFAULT_SCHEMA_NAME, default_table_name=DEFAULT_TABLE_NAME,
                               default_id_column_name=DEFAULT_ID_COLUMN_NAME,
                               is_main_column_name=DEFAULT_IS_MAIN_COLUMN_NAME,
                               is_test_data=is_test_data)

    def insert_group(self, group_dict: Dict[str, any], ignore_duplicate: bool = False,
                     lang_code: LangCode = None) -> tuple[int, int]:
        """
            Returns the new group_id
            group_dict has to include the following
            for group_ml_table:
            title: str, lang_code: str = None,
            is_main_title: bool = True,
            "description": None,
            is_title_approved: bool = None,
            is_description_approved: bool = None
            for group_table:
            name: str,
            hashtag: str = None,
            is_approved: bool = False,
            parent_group_id: str = None,
            is_interest: bool = None,
            non_members_visibility_id: int = 1, members_visibility_id: int = 1,
            created_user_id: int = 0
            example of group_dict:
            {
                "title": "title",
                "lang_code": "en",
                "name": "name",
                "hashtag": "hashtag",
                "is_approved": True,
                "parent_group_id": 1,
                "is_interest": True,
                "non_members_visibility_id": 1,
                "members_visibility_id": 1,
                "description": "description",
                "is_title_approved": True,
                "is_description_approved": True,
                "created_user_id": 1
            }
        """
        logger.start(object={'data': str(group_dict)})
        group_data_json = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved', None),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
        }

        group_id = GenericCRUDML.insert(self, data_json=group_data_json, ignore_duplicate=ignore_duplicate)

        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
        group_ml_data_json = {
            "lang_code": lang_code.value,
            "group_id": group_id,
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', False),
            "description": group_dict.get('description'),
            "created_user_id": user_context.get_effective_user_id(),
            "created_real_user_id": user_context.get_real_user_id(),
            "created_effective_user_id": user_context.get_effective_user_id(),
            "created_effective_profile_id": user_context.get_effective_profile_id(),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved', None),
            "is_description_approved": group_dict.get('is_description_approved', None)
        }
        group_ml_id = GenericCRUDML.insert(self, table_name="group_ml_table", data_json=group_ml_data_json,
                                           ignore_duplicate=ignore_duplicate)

        logger.end(object={'group_id': group_id, 'group_ml_id': group_ml_id})
        return group_id, group_ml_id

    def upsert_group(self, group_dict: Dict[str, any], data_json_compare: dict = None,
                     lang_code: LangCode = None,
                     order_by: str = "") -> dict:
        """
            Returns the new group_id
            group_dict has to include the following
            for group_ml_table:
            title: str, lang_code: str = None,
            is_main_title: bool = True,
            "description": None,
            is_title_approved: bool = False,
            is_description_approved: bool = False
            for group_table:
            name: str,
            hashtag: str = None,
            is_approved: bool = None,
            parent_group_id: str = None,
            is_interest: bool = None,
            non_members_visibility_id: int = 1, members_visibility_id: int = 1
            created_user_id: int = 0
            example of group_dict:
            {
                "title": "title",
                "lang_code": "en",
                "name": "name",
                "hashtag": "hashtag",
                "is_approved": True,
                "parent_group_id": 1,
                "is_interest": True,
                "non_members_visibility_id": 1,
                "members_visibility_id": 1,
                "description": "description",
                "is_title_approved": True,
                "is_description_approved": True,
                "created_user_id": 1
            }
        """
        logger.start(object={'data': str(group_dict)})
        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
        if not data_json_compare:
            data_json_compare = {
                "name": group_dict.get('name'),
            }
        group_data_json = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved', None),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
        }

        group_ml_data_json = {
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', False),
            "description": group_dict.get('description'),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved', None),
            "is_description_approved": group_dict.get('is_description_approved', None)
        }
        if "(" and ")" in group_dict.get('title'):
            group_id, group_ml_ids_list = GenericCRUDML.upsert_value_with_abbreviations(
                self, table_name="group_table", data_json=group_ml_data_json,
                data_ml_json=group_ml_data_json,
                ml_table_name="group_ml_table",
                lang_code=lang_code,
                data_json_compare=data_json_compare,
                compare_view_name="group_ml_also_not_approved_view",
                order_by=order_by
            )
        else:
            group_id, group_ml_id = GenericCRUDML.upsert_value(
                self, data_json=group_data_json, data_ml_json=group_ml_data_json,
                ml_table_name="group_ml_table", data_json_compare=data_json_compare,
                lang_code=lang_code, compare_view_name="group_ml_also_not_approved_view",
                order_by=order_by
            )
            group_ml_ids_list = [group_ml_id]
        upsert_information = {
            "group_id": group_id,
            "group_ml_ids_list": group_ml_ids_list
        }

        # TODO Shall we add upsert_informaiton to the logger.end()?
        logger.end(object={'group_id': group_id, 'group_ml_ids_list': group_ml_ids_list})
        return upsert_information

    def update_group(self, group_id: int, group_dict: Dict[str, any], lang_code: LangCode = None) -> None:
        logger.start(object={'group_id': group_id, 'data': str(group_dict)})
        group_data_json = {
            "name": group_dict.get('name'),
            "hashtag": group_dict.get('hashtag'),
            "is_approved": group_dict.get('is_approved', None),
            "parent_group_id": group_dict.get('parent_group_id'),
            "is_interest": group_dict.get('is_interest'),
            "non_members_visibility_id": group_dict.get('non_members_visibility_id', 1),
            "members_visibility_id": group_dict.get('members_visibility_id', 1),
        }
        GenericCRUDML.update_by_id(self, id_column_value=group_id, data_json=group_data_json)
        if not lang_code:
            lang_code = group_dict.get('lang_code') or LangCode.detect_lang_code(group_dict.get('title'))
        group_ml_data_json = {
            "group_id": group_id,
            "lang_code": lang_code.value,
            "title": group_dict.get('title'),
            "is_main_title": group_dict.get('is_main_title', True),
            "description": group_dict.get('description'),
            "updated_user_id": user_context.get_effective_user_id(),
            "updated_real_user_id": user_context.get_real_user_id(),
            "updated_effective_user_id": user_context.get_effective_user_id(),
            "updated_effective_profile_id": user_context.get_effective_profile_id(),
            "is_title_approved": group_dict.get('is_title_approved', None),
            "is_description_approved": group_dict.get('is_description_approved', None)
        }
        GenericCRUDML.update_by_id(self, table_name="group_ml_table",
                                   id_column_value=group_id, data_json=group_ml_data_json,
                                   id_column_name="group_ml_id")
        logger.end()

    def get_group_dict_by_group_id(self, group_id: int, group_ml_id: int = None) -> Dict[str, any]:
        logger.start(object={'group_id': group_id})
        group_ml_dict = {}
        if group_ml_id:
            group_ml_dict = self.select_one_dict_by_id(view_table_name="group_ml_also_not_approved_view",
                                                       id_column_value=group_ml_id,
                                                       id_column_name="group_ml_id")
        group_dict = self.select_one_dict_by_id(view_table_name="group_view", id_column_value=group_id,
                                                id_column_name="group_id")
        logger.end(object={'group_ml_dict': str(group_ml_dict), 'group_view': str(group_dict)})
        return {**group_dict, **group_ml_dict}

    def delete_by_group_id(self, group_id: int, group_ml_id: int = None) -> None:
        logger.start(object={'group_id': group_id})
        # Delete from group_table
        self.delete_by_id(table_name="group_table", id_column_name="group_id", id_column_value=group_id)
        # Delete from group_ml_table
        if group_ml_id:
            self.delete_by_id(table_name="group_ml_table", id_column_name="group_ml_id", id_column_value=group_ml_id)
        logger.end()

    def get_groups_by_group_title(self, group_title: str) -> list:
        logger.start(object={'group_title': group_title})
        groups = []
        group_ids_dicts_list = self.select_multi_dict_by_id(
            view_table_name="group_ml_also_not_approved_view", id_column_value=group_title, id_column_name="title",
            select_clause_value="group_id, group_ml_id")
        for group_ids_dict in group_ids_dicts_list:
            group_dict = self.get_group_dict_by_group_id(group_ids_dict.get('group_id'), group_ids_dict.get('group_ml_id'))
            groups.append(group_dict)
        logger.end(object={'groups': str(groups)})
        return groups
