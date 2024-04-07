import re
from typing import Any
from typing import Optional

from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger
from user_context_remote.user_context import UserContext

from .constants import DEFAULT_SQL_SELECT_LIMIT, LOGGER_CRUD_ML_CODE_OBJECT
from .generic_crud import GenericCRUD
from .utils import validate_select_table_name

IS_MAIN_COLUMN_NAME = "is_main"


class GenericCRUDML(GenericCRUD, metaclass=MetaLogger, object=LOGGER_CRUD_ML_CODE_OBJECT):
    """A class that provides generic CRUD functionality for tables with multi-language support."""

    def __init__(self, default_schema_name: str, default_table_name: str = None,
                 default_id_column_name: str = None,
                 is_main_column_name: str = IS_MAIN_COLUMN_NAME,
                 is_test_data: bool = False) -> None:
        """Initializes the GenericCRUDML class. If connection is not provided,
        a new connection will be created."""
        if default_table_name is not None:
            self.default_ml_table_name = self._create_ml_table_name(default_table_name)
            self.default_view_table_name = self._get_ml_view_name(default_table_name)
        else:
            self.default_ml_table_name = None
            self.default_view_table_name = None
        self.logger.info("GenericCRUDML.__init__", object={"default_ml_table_name": self.default_ml_table_name,
                                                           "default_view_table_name": self.default_view_table_name})
        GenericCRUD.__init__(self, default_schema_name=default_schema_name,
                             default_table_name=default_table_name,
                             default_view_table_name=self.default_view_table_name,
                             default_id_column_name=default_id_column_name,
                             is_test_data=is_test_data)
        self.user_context = UserContext()
        # TODO: we may have to change it to a list when we will have multiple is_main columns
        self.is_main_column_name = is_main_column_name

    def sql_in_list_by_entity_list_id(self, schema_name: str, entity_name: str, entity_list_id: int) -> str:
        """Example: select group_id from group.group_list_member_table WHERE group_list_id=1"""

        old_schema_name = self.schema_name
        self.set_schema(schema_name=schema_name)
        ids = self.select_multi_dict_by_id(view_table_name=f"{entity_name}_list_member_view",
                                           select_clause_value=f"{entity_name}_id",
                                           id_column_name=f"{entity_name}_list_id",
                                           id_column_value=entity_list_id)
        if ids:
            result = f" IN ({','.join([str(_id[f'{entity_name}_id']) for _id in ids])})"
        else:
            result = " = TRUE"
        self.set_schema(schema_name=old_schema_name)

        return result

    def add_value(self, data_ml_json: dict, table_id: int = None, lang_code: LangCode = None,
                  is_main: int = 0, data_json: dict = None, table_name: str = None,
                  ml_table_name: str = None, schema_name: str = None) -> Optional[tuple]:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code, data_ml_json=data_ml_json)
        old_schema_name = self.schema_name
        self.schema_name = schema_name or self.schema_name
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name

        old_cursor = self.cursor
        try:
            cursor = self.connection.cursor()
            self.cursor = cursor

            # if this is the first insert of this data, is_main should be 1
            if table_id is None:
                is_main = 1
            elif is_main == 1:
                self._update_old_main_value_to_zero(table_id, table_name)

            # id is the id value of the row in the table_name table
            table_id = table_id or self.insert(data_json=data_json, ignore_duplicate=True,
                                               table_name=table_name, commit_changes=False)
            if table_id is None:  # TODO: delete
                self.logger.error("Error inserting data_json", object={"data_json": str(data_json)})
                self.connection.rollback()
                return None

            if data_ml_json is None or data_ml_json == {}:
                self.connection.commit()
                return table_id, None

            id_column_name = re.sub(r'(_table)$', '_id', table_name)
            data_ml_json[id_column_name] = table_id
            data_ml_json["lang_code"] = lang_code_str
            data_ml_json[self.is_main_column_name] = is_main

            # ml_id is the id value of the row in the ml_table_name table
            ml_table_id = self.insert(data_json=data_ml_json, table_name=ml_table_name, ignore_duplicate=True,
                                      commit_changes=False)

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            self.cursor = old_cursor
            self.schema_name = old_schema_name
            cursor.close()
        return table_id, ml_table_id

    def add_value_if_not_exist(self, data_ml_json: dict, table_id: int = None, lang_code: LangCode = None,
                               is_main: int = 0, data_json: dict = None, table_name: str = None,
                               ml_table_name: str = None, schema_name: str = None,
                               order_by: str = None) -> tuple:
        self.schema_name = schema_name or self.schema_name
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name
        id_column_name = GenericCRUD.generate_id_column_name(table_name)
        ml_id_column_name = GenericCRUD.generate_id_column_name(ml_table_name)

        # check if the row exists in the ml_table
        name = data_ml_json.get("title") or data_ml_json.get("name")
        if not name:
            raise ValueError("name or title is required for upsert_value")
        table_id = table_id or self.get_id_by_name(table_name=table_name, ml_table_name=ml_table_name, name=name,
                                                   lang_code=lang_code,
                                                   id_column_name=id_column_name, order_by=order_by)
        ml_table_id = self.get_ml_id_by_name(ml_table_name=ml_table_name, name=name, lang_code=lang_code,
                                             id_column_name=ml_id_column_name, order_by=order_by)
        if not table_id:
            return self.add_value(data_ml_json=data_ml_json, table_id=table_id, lang_code=lang_code, is_main=is_main,
                                  data_json=data_json, table_name=table_name, ml_table_name=ml_table_name)
        else:
            return table_id, ml_table_id

    def update_value_by_id(self, data_ml_json: dict, ml_table_id: int, table_id: int,
                           lang_code: LangCode = None, is_main: int = 0, data_json: dict = None,
                           table_name: str = None, ml_table_name: str = None,
                           schema_name: str = None, limit: int = DEFAULT_SQL_SELECT_LIMIT,
                           order_by: str = None) -> tuple:
        old_schema_name = self.schema_name
        self.schema_name = schema_name or self.schema_name
        lang_code_str = self._get_lang_code_str(lang_code=lang_code, data_ml_json=data_ml_json)
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name
        id_column_name = GenericCRUD.generate_id_column_name(table_name)

        if table_id is None:
            raise ValueError("table_id is required for update_value")
        if ml_table_id is None:
            raise ValueError("ml_table_id is required for update_value")

        old_cursor = self.cursor
        try:
            cursor = self.connection.cursor()
            self.cursor = cursor

            if is_main == 1:
                self._update_old_main_value_to_zero(table_id, table_name)
            if data_json:
                self.update_by_id(data_json=data_json, table_name=table_name, id_column_name=id_column_name,
                                  id_column_value=table_id, limit=limit, order_by=order_by, commit_changes=False)

            data_ml_json[id_column_name] = table_id
            data_ml_json["lang_code"] = lang_code_str
            data_ml_json[self.is_main_column_name] = is_main
            id_column_name = GenericCRUD.generate_id_column_name(ml_table_name)

            self.update_by_id(data_json=data_ml_json, table_name=ml_table_name, id_column_name=id_column_name,
                              id_column_value=ml_table_id, limit=limit, order_by=order_by, commit_changes=False)

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            self.cursor = old_cursor
            self.schema_name = old_schema_name
            cursor.close()
        return table_id, ml_table_id

    def upsert_value(self, data_ml_json: dict, table_id: int = None, 
                     data_json_compare: dict = None, lang_code: LangCode = None,
                     is_main: int = 0, data_json: dict = None, table_name: str = None,
                     ml_table_name: str = None, schema_name: str = None,
                     compare_view_name: str = None,
                     limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> tuple:
        self.schema_name = schema_name or self.schema_name
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name
        id_column_name = GenericCRUD.generate_id_column_name(table_name)
        ml_id_column_name = GenericCRUD.generate_id_column_name(ml_table_name)

        # check if the row exists in the ml_table
        name = data_ml_json.get("title") or data_ml_json.get("name")
        name_compare = name
        if not name:
            raise ValueError("name or title is required for upsert_value")
        if data_json_compare:
            name_compare = data_json_compare.get("title") or data_json_compare.get("name")

        table_id = table_id or self.get_id_by_name(table_name=table_name, ml_table_name=ml_table_name, name=name_compare,
                                                   lang_code=lang_code, compare_view_name=compare_view_name,
                                                   id_column_name=id_column_name, order_by=order_by)
        ml_table_id = self.get_ml_id_by_name(ml_table_name=ml_table_name, name=name_compare, lang_code=lang_code,
                                             compare_view_name=compare_view_name,
                                             id_column_name=ml_id_column_name, order_by=order_by)
        if not table_id:
            return self.add_value(data_ml_json=data_ml_json, table_id=table_id, lang_code=lang_code, is_main=is_main,
                                  data_json=data_json, table_name=table_name, ml_table_name=ml_table_name)
        else:
            return self.update_value_by_id(data_ml_json=data_ml_json, ml_table_id=ml_table_id, table_id=table_id,
                                           lang_code=lang_code, is_main=is_main, data_json=data_json,
                                           table_name=table_name,
                                           ml_table_name=ml_table_name, schema_name=schema_name,
                                           limit=limit, order_by=order_by)

    def upsert_value_with_abbreviations(self, data_ml_json: dict,  data_json_compare: dict = None,
                                        table_id: int = None, lang_code: LangCode = None,
                                        data_json: dict = None, table_name: str = None,
                                        ml_table_name: str = None, schema_name: str = None,
                                        compare_view_name: str = None,
                                        limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> tuple:
        self.schema_name = schema_name or self.schema_name
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name
        id_column_name = GenericCRUD.generate_id_column_name(table_name)
        ml_id_column_name = GenericCRUD.generate_id_column_name(ml_table_name)

        # check if the row exists in the ml_table
        name_and_abbreviations = data_ml_json.get("title") or data_ml_json.get("name")
        if not name_and_abbreviations:
            raise ValueError("name or title is required for upsert_value")
        if data_json_compare:
            name_and_abbreviations_compare = data_json_compare.get("title") or data_json_compare.get("name")
        else:
            name_and_abbreviations_compare = name_and_abbreviations

        name = name_and_abbreviations.split(" (")[0]
        name_compare = name_and_abbreviations_compare.split(" (")[0]
        abbreviations = name_and_abbreviations.split(" (")[1][:-1]
        abbreviations_list = abbreviations.split(", ")
        data_ml_json_with_name = data_ml_json.copy()
        data_ml_json_with_name["title"] = name
        data_ml_json_with_abbreviation_list = []
        for abbreviation in abbreviations_list:
            data_ml_json_with_abbreviation = data_ml_json.copy()
            data_ml_json_with_abbreviation["title"] = abbreviation
            data_ml_json_with_abbreviation_list.append(data_ml_json_with_abbreviation)

        table_id = table_id or self.get_id_by_name(table_name=table_name, ml_table_name=ml_table_name, name=name_compare,
                                                   lang_code=lang_code, compare_view_name=compare_view_name,
                                                   id_column_name=id_column_name, order_by=order_by)
        ml_table_id = self.get_ml_id_by_name(ml_table_name=ml_table_name, name=name_compare, lang_code=lang_code,
                                             compare_view_name=compare_view_name,
                                             id_column_name=ml_id_column_name, order_by=order_by)
        ml_ids_list = []
        if not table_id:
            table_id, ml_table_id = self.add_value(data_ml_json=data_ml_json_with_name, table_id=table_id, lang_code=lang_code,
                                                   is_main=1, data_json=data_json, table_name=table_name,
                                                   ml_table_name=ml_table_name)
            ml_ids_list.append(ml_table_id)
            for data_ml_json_with_abbreviation in data_ml_json_with_abbreviation_list:
                table_id, ml_table_id = self.add_value(data_ml_json=data_ml_json_with_abbreviation, table_id=table_id,
                                                       lang_code=lang_code, is_main=0, data_json=data_json,
                                                       table_name=table_name, ml_table_name=ml_table_name)
                ml_ids_list.append(ml_table_id)
        else:
            ml_ids_list = self.get_ml_ids_by_id(table_id=table_id, ml_table_name=ml_table_name, lang_code=lang_code,
                                                id_column_name=id_column_name, ml_id_column_name=ml_id_column_name,
                                                compare_view_name=compare_view_name,
                                                order_by=order_by)
            ml_ids_list.remove(ml_table_id)
            table_id, main_ml_table_id = self.update_value_by_id(data_ml_json=data_ml_json_with_name, ml_table_id=ml_table_id,
                                                                 table_id=table_id,
                                                                 lang_code=lang_code, is_main=1, data_json=data_json,
                                                                 table_name=table_name,
                                                                 ml_table_name=ml_table_name, schema_name=schema_name,
                                                                 limit=limit, order_by=order_by)
            for index, data_ml_json_with_abbreviation in enumerate(data_ml_json_with_abbreviation_list):
                if index < len(ml_ids_list):
                    table_id, ml_table_id = self.update_value_by_id(data_ml_json=data_ml_json_with_abbreviation,
                                                                    ml_table_id=ml_ids_list[index], table_id=table_id,
                                                                    lang_code=lang_code, is_main=0, data_json=data_json,
                                                                    table_name=table_name,
                                                                    ml_table_name=ml_table_name, schema_name=schema_name,
                                                                    limit=limit, order_by=order_by)
                else:
                    table_id, ml_table_id = self.add_value(data_ml_json=data_ml_json_with_abbreviation, table_id=table_id,
                                                           lang_code=lang_code, is_main=0, data_json=data_json,
                                                           table_name=table_name, ml_table_name=ml_table_name)
                ml_ids_list.append(ml_table_id)
            ml_ids_list.append(main_ml_table_id)
        return table_id, ml_ids_list

    def get_values_tuple(self, table_id: int, lang_code: LangCode = None,
                         id_column_name: str = None, select_clause_value: str = "*",
                         order_by: str = None) -> tuple:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code)
        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(
            self.default_table_name)
        result = self.select_one_tuple_by_where(where=f"{id_column_name}=%s AND lang_code=%s",
                                                params=(table_id, lang_code_str),
                                                select_clause_value=select_clause_value,
                                                order_by=order_by)

        return result

    def get_values_dict(self, table_id: int, lang_code: LangCode = None,
                        id_column_name: str = None,
                        order_by: str = None) -> dict:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code)
        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(
            self.default_table_name)
        result = self.select_one_dict_by_where(where=f"{id_column_name}=%s AND lang_code=%s",
                                               params=(table_id, lang_code_str),
                                               order_by=order_by or f"{id_column_name} DESC")

        return result

    def get_values_dict_list(self, table_id: int, lang_code: LangCode = None,
                             id_column_name: str = None,
                             order_by: str = None) -> list:
        lang_code_str = self._get_lang_code_str(lang_code=lang_code)
        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(
            self.default_table_name)
        result = self.select_multi_dict_by_where(where=f"{id_column_name}=%s AND lang_code=%s",
                                                 params=(table_id, lang_code_str),
                                                 order_by=order_by)
        return result

    def get_main_values_tuple(self, table_id: int, id_column_name: str = None, select_clause_value: str = "*",
                              order_by: str = None) -> tuple:

        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(
            self.default_table_name)
        result = self.select_one_tuple_by_where(where=f"{id_column_name}=%s AND is_main=1",
                                                params=(table_id,),
                                                select_clause_value=select_clause_value,
                                                order_by=order_by or f"{id_column_name} DESC")

        return result

    def get_main_values_dict(self, table_id: int, id_column_name: str = None, select_clause_value: str = "*",
                             order_by: str = None) -> dict:

        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(
            self.default_table_name)
        result = self.select_one_dict_by_where(where=f"{id_column_name}=%s AND is_main=1",
                                               params=(table_id,),
                                               select_clause_value=select_clause_value,
                                               order_by=order_by)

        return result

    def get_id_by_name(self, name: str, table_name: str = None, ml_table_name: str = None, lang_code: LangCode = None,
                       id_column_name: str = None, order_by: str = None,
                       compare_view_name: str = None) -> Optional[int]:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code, name=name)
        table_name = table_name or self.default_table_name
        ml_table_name = ml_table_name or self.default_ml_table_name
        compare_view_name = compare_view_name or self._get_view_name(ml_table_name)
        id_column_name = id_column_name or GenericCRUD.generate_id_column_name(table_name)
        if GenericCRUD.is_column_in_table(self, table_name=ml_table_name, column_name="title"):
            result = self.select_one_tuple_by_where(view_table_name=compare_view_name,
                                                    select_clause_value=id_column_name,
                                                    where="title=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        else:
            result = self.select_one_tuple_by_where(view_table_name=compare_view_name,
                                                    select_clause_value=id_column_name,
                                                    where="`name`=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        if result:
            return result[0]
        else:
            return None

    def get_ml_id_by_name(self, name: str, ml_table_name: str = None, lang_code: LangCode = None,
                          id_column_name: str = None, order_by: str = None,
                          compare_view_name: str = None) -> Optional[int]:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code, name=name)
        ml_table_name = ml_table_name or self.default_ml_table_name
        compare_view_name = compare_view_name or self._get_view_name(ml_table_name)
        ml_id_column_name = id_column_name or GenericCRUD.generate_id_column_name(ml_table_name)
        if GenericCRUD.is_column_in_table(self, table_name=ml_table_name, column_name="title"):
            result = self.select_one_tuple_by_where(view_table_name=compare_view_name,
                                                    select_clause_value=ml_id_column_name,
                                                    where="title=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        else:
            result = self.select_one_tuple_by_where(view_table_name=compare_view_name,
                                                    select_clause_value=ml_id_column_name,
                                                    where="`name`=%s AND lang_code=%s",
                                                    params=(name, lang_code_str),
                                                    order_by=order_by)
        if result:
            return result[0]
        else:
            return None

    def get_ml_ids_by_id(self, table_id: int, ml_table_name: str = None, lang_code: LangCode = None,
                         id_column_name: str = None, ml_id_column_name: str = None, order_by: str = None,
                         compare_view_name: str = None) -> list:
        lang_code_str = None if lang_code is None else lang_code.value
        compare_view_name = compare_view_name or self._get_view_name(ml_table_name)
        result = self.select_multi_tuple_by_where(view_table_name=compare_view_name,
                                                  select_clause_value=ml_id_column_name,
                                                  where=f"{id_column_name}=%s AND lang_code=%s",
                                                  params=(table_id, lang_code_str),
                                                  order_by=order_by)
        return [row[0] for row in result]

    def delete_by_name(self, name: str,
                       lang_code: LangCode = None) -> None:

        lang_code_str = self._get_lang_code_str(lang_code=lang_code, name=name)
        if GenericCRUD.is_column_in_table(self, table_name=self.default_view_table_name, column_name="title"):
            self.delete_by_where(table_name=self.default_ml_table_name, where="title=%s AND lang_code=%s",
                                 params=(name, lang_code_str))
        else:
            self.delete_by_where(table_name=self.default_ml_table_name, where="`name`=%s AND lang_code=%s",
                                 params=(name, lang_code_str))

    @staticmethod
    def _create_ml_table_name(table_name: str) -> str:
        ml_table_name = re.sub(r'(_table)$', '_ml_table', table_name)
        return ml_table_name

    @staticmethod
    def _get_ml_view_name(table_name: str) -> str:
        view_name = re.sub(r'(_table)$', '_ml_view', table_name)
        return view_name

    # Change the old row with is_main=1 to is_main=0
    def _update_old_main_value_to_zero(self, table_id: int, table_name: str) -> None:

        data_ml_json = {self.is_main_column_name: 0}
        id_column_name = GenericCRUD.generate_id_column_name(table_name)
        self.update_by_where(table_name=self.default_ml_table_name,
                             data_json=data_ml_json,
                             where=f"{id_column_name}=%s AND is_main=1",
                             params=(table_id,))

    def _get_lang_code_str(self, name: str = None, lang_code: LangCode = None,
                           data_ml_json: dict = None) -> str:
        if lang_code is None and name is not None:
            lang_code_str = LangCode.detect_lang_code_str(name)
        elif lang_code is None and data_ml_json is not None:
            text = data_ml_json.get("title") or data_ml_json.get("name")
            lang_code_str = LangCode.detect_lang_code_str(text)
        elif lang_code is None:
            lang_code_str = self.user_context.get_effective_profile_preferred_lang_code_string()
        else:
            lang_code_str = lang_code.value
        return lang_code_str

    # The follwing methods may be irrelevant since GenericCRUD has equivalent methods
    # TODO: We may want to remove these following methods

    # This method returns the value in a selected column by a condition, the condition can be none or a value
    # for a specific column
    def select_one_by_value_with_none_option(
            self, condition_column_name, condition_column_value,
            view_table_name: str = None,
            select_column_name: str = None) -> Any:
        view_table_name = view_table_name or self.default_view_table_name
        # Returns the row id if select_column_name is None
        select_column_name = select_column_name or self.default_column
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""

        self.logger.warning("this method is deprecated, use select_one_tuple_by_id instead")
        validate_select_table_name(view_table_name)
        select_query = f"SELECT {select_column_name} " f"FROM {self.schema_name}.{view_table_name} " + (
            f"WHERE `{condition_column_name}` = \"{condition_column_value}\" " if (condition_column_name and
                                                                                   condition_column_value)
            else f"WHERE `{condition_column_name}` IS NULL ")

        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        # Extract the first element from the first tuple in the result
        result = result[0][0] if result else None

        return result

    def select_multi_tuple_by_value_with_none_option(self,
                                                     condition_column_name,
                                                     condition_column_value,
                                                     view_table_name: str = None, select_clause_value: str = "*",

                                                     limit: int = DEFAULT_SQL_SELECT_LIMIT,
                                                     order_by: str = None) -> list:
        view_table_name = view_table_name or self.default_view_table_name
        # Returns the row id if select_column_name is None
        select_column_name = f"`{select_clause_value}`" if select_clause_value != "*" else "*"
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""

        self.logger.warning("this method is deprecated, use select_multi_tuple_by_id instead")
        validate_select_table_name(view_table_name)
        select_query = f"SELECT {select_column_name} " f"FROM {self.schema_name}.{view_table_name} " + (
            f"WHERE `{condition_column_name}` = \"{condition_column_value}\" " if (condition_column_name and
                                                                                   condition_column_value)
            else f"WHERE {condition_column_name} IS NULL ") + (
            f"ORDER BY {order_by} " if order_by else "") + f"LIMIT {limit}"
        self.cursor.execute(select_query)
        result = self.cursor.fetchall()
        return result

    def select_multi_dict_by_value_with_none_option(self,
                                                    condition_column_name,
                                                    condition_column_value,
                                                    view_table_name: str = None, select_clause_value: str = "*",

                                                    limit: int = DEFAULT_SQL_SELECT_LIMIT,
                                                    order_by: str = None) -> list:
        self.logger.warning("this method is deprecated, use select_multi_tuple_by_id instead")
        """Selects a column from the table based on a WHERE clause and returns it as a list of dictionaries."""
        result = self.select_multi_tuple_by_value_with_none_option(condition_column_name, condition_column_value,

                                                                   view_table_name=view_table_name,
                                                                   select_clause_value=select_clause_value,
                                                                   limit=limit, order_by=order_by)
        return [self.convert_to_dict(row, select_clause_value) for row in result]