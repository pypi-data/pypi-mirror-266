import time
import json
from functools import reduce

import pandas as pd

from notion_client import Client, APIErrorCode, APIResponseError
from notion_client.errors import HTTPResponseError, RequestTimeoutError
from notion_client.helpers import collect_paginated_api


class NotionMaxAttempsException(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class Notion2PandasClient(Client):
    """Extension of Client from notion_client.

    Attributes:
        secondsToRetry: .
        callsLimitThreshold: .
        maxAttempsExecutoner: .
    """

    _ROW_HASH_KEY = 'Row_Hash'
    _ROW_PAGEID_KEY = 'PageID'

    # It's not in the official documentation, but it seems there is a limit of 2700 API calls in 15 minutes.
    # https://notionmastery.com/pushing-notion-to-the-limits/#rate-limits
    # WIP
    _RATE_LIMIT_THRESHOLD = 900 #60 * 15
    _CALLS_LIMIT_THRESHOLD = 2700

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.secondsToRetry = kwargs['secondsToRetry'] if 'secondsToRetry' in kwargs else 150
        self.maxAttempsExecutioner = kwargs['maxAttempsExecutioner'] if 'maxAttempsExecutioner' in kwargs else 5
        
        self.read_only_columns = {"last_edited_time", "last_edited_time",
                                  "files", "created_time", "rollup", "unique_id", "last_edited_by",
                                  "button", "formula", "created_by"}

        self.title_read_write_lambdas = (lambda notion_property:
                                         notion_property.get('title')[
                                             0].get("plain_text")
                                         if len(notion_property.get('title')) > 0
                                         else '',
                                         lambda row_value: {
                                             "title": [{"type": "text", "text": {"content": row_value}}]}
                                         if row_value != ''
                                         else {"title": []})
        self.rich_text_read_write_lambdas = (lambda notion_property:
                                             notion_property.get('rich_text')[
                                                 0].get("plain_text")
                                             if len(notion_property.get('rich_text')) > 0
                                             else '',
                                             lambda row_value: {"rich_text": [
                                                 {"type": "text", "text": {"content": row_value}}]}
                                             if row_value != '' else {"rich_text": []})
        self.checkbox_read_write_lambdas = (lambda notion_property:
                                            notion_property.get('checkbox'),
                                            lambda row_value: {'checkbox': row_value})
        self.created_time_read_write_lambdas = (lambda notion_property:
                                                notion_property.get(
                                                    'created_time'),
                                                lambda row_value: 'Not supported from API')
        self.number_read_write_lambdas = (lambda notion_property:
                                          notion_property.get('number'),
                                          lambda row_value: {
                                              'number': row_value}
                                          if pd.notna(row_value) else {'number': None})
        self.email_read_write_lambdas = (lambda notion_property:
                                         notion_property.get('email')
                                         if notion_property.get('email') is not None
                                         else '',
                                         lambda row_value: {'email': row_value}
                                         if row_value != ''
                                         else {'email': None})
        self.url_read_write_lambdas = (lambda notion_property:
                                       notion_property.get('url')
                                       if notion_property.get('url') is not None
                                       else '',
                                       lambda row_value: {'url': row_value}
                                       if row_value != ''
                                       else {'url': None})
        self.multi_select_read_write_lambdas = (lambda notion_property:
                                                str(list(map(lambda notion_select: notion_select.get('name'),
                                                             notion_property.get('multi_select')))),
                                                lambda row_value: {"multi_select": list(map(lambda notion_select:
                                                                                            {"name": notion_select}, eval(row_value)))
                                                                   if row_value != '' else []})
        self.select_read_write_lambdas = (lambda notion_property:
                                          notion_property.get(
                                              'select').get('name')
                                          if notion_property.get('select') is not None
                                          else '',
                                          lambda row_value: {
                                              'select': {'name': row_value}}
                                          if row_value != ''
                                          else {'select': None})
        self.date_read_write_lambdas = (lambda notion_property:
                                        notion_property.get('date')
                                        if notion_property.get('date') is not None
                                        else '',
                                        lambda row_value:
                                        {"date": row_value
                                            if row_value != ''
                                            else None})
        self.files_read_write_lambdas = (lambda notion_property:
                                         reduce(lambda x, y: x + ';' + y, list(map(lambda notion_file: notion_file.get(
                                             'file').get('url'), notion_property.get('files'))))
                                         if notion_property.get('files')
                                         else '',
                                         lambda row_value: 'Not supported from API')
        self.formula_read_write_lambdas = (lambda notion_property:
                                           self.__readValueFromNotion(
                                               notion_property.get('formula')),
                                           lambda row_value: 'Not supported from API')
        self.phone_number_read_write_lambdas = (lambda notion_property: notion_property.get('phone_number') if notion_property.get('phone_number') is not None else '',
                                                lambda row_value: {'phone_number': row_value} if row_value != '' else {'phone_number': None})
        self.status_read_write_lambdas = (lambda notion_property:
                                          notion_property.get(
                                              'status').get('name'),
                                          lambda row_value: {'status': {"name": row_value}})
        self.unique_id_read_write_lambdas = (lambda notion_property:
                                             (notion_property.get('unique_id').get('prefix') + notion_property.get('unique_id').get('number')
                                              if notion_property.get('unique_id').get('prefix') is not None
                                                 else notion_property.get('unique_id').get('number')),
                                             lambda row_value: 'Not supported from API')
        self.created_by_read_write_lambdas = (lambda notion_property:
                                              notion_property.get(
                                                  'created_by').get('id'),
                                              lambda row_value: 'Not supported from API')
        self.last_edited_time_read_write_lambdas = (lambda notion_property:
                                                    notion_property.get(
                                                        'last_edited_time'),
                                                    lambda row_value: 'Not supported from API')
        self.string_read_write_lambdas = (lambda notion_property:
                                          notion_property.get('string'),
                                          lambda row_value: {'string': row_value} if row_value != ''
                                          else {'string': None})
        self.last_edited_by_read_write_lambdas = (lambda notion_property:
                                                  notion_property.get(
                                                      'last_edited_by').get('id'),
                                                  lambda row_value: 'Not supported from API')
        self.button_read_write_lambdas = (lambda notion_property:
                                          'Not supported from API',
                                          lambda row_value: 'Not supported from API')
        self.relation_read_write_lambdas = (lambda notion_property:
                                            str(list(map(lambda notion_relation: notion_relation.get(
                                                'id'), notion_property.get('relation')))),
                                            lambda row_value:
                                            {"relation": list(map(lambda notion_relation: {"id": notion_relation}, eval(row_value)))
                                             if row_value != ''
                                             else []})
        self.rollup_read_write_lambdas = (lambda notion_property:
                                          str(list(map(lambda notion_rollup: self.__readValueFromNotion(
                                              notion_rollup), notion_property.get('rollup').get('array')))),
                                          lambda row_value: 'Not supported from API')
        self.people_read_write_lambdas = (lambda notion_property:
                                          str(list(map(lambda notion_person: notion_person.get(
                                              'id'), notion_property.get('people')))),
                                          lambda row_value: {"people": list(map(lambda notion_people: {"id": notion_people, 'object': 'user'}, eval(row_value)))
                                                             if row_value != '' else []})
        
    """Since Notion has introduced limits on requests to their APIs (https://developers.notion.com/reference/request-limits), 
       this method can repeat the request to the Notion APIs at predefined time intervals
       until a result is obtained or if the maximum limit of attempts is reached."""
    def _notionExecutor(self, api_to_call, **kwargs):
        attempts = self.maxAttempsExecutioner
        current_calls = 0
        while (attempts > 0):
            try:
                result = api_to_call(**kwargs)
                current_calls += 1
                return result
            except HTTPResponseError as error:
                print('Catched exception: ' + str(error))
                attempts -= 1
                if isinstance(error, APIResponseError):
                    print('Error code: ' + error.code)
                    if error.code != APIErrorCode.InternalServerError and error.code != APIErrorCode.ServiceUnavailable:
                        print(error)
                        print(APIResponseError)
                        # raise APIErrorCode.ObjectNotFound
                else:
                    # Other error handling code
                    print(error)
                # Wait secondsToRetry before retry
                time.sleep(self.secondsToRetry)
            except RequestTimeoutError as error:
                print('Catched exception: ' + str(error))
                attempts -= 1
            if attempts == 0:
                raise NotionMaxAttempsException(
                    "NotionMaxAttempsException") from None
            print('[_notionExecutor] Remaining attemps: ' + str(attempts))
        return result

    def get_database_columns(self, database_ID):
        return self._notionExecutor(
            self.databases.retrieve, **{'database_id': database_ID})

    def create_page(self, parent_id, properties = None):
        created_page = self._notionExecutor(self.pages.create, **{'parent' : {"database_id": parent_id},
         'properties' : properties})
        return created_page.get('id')

    def update_page(self, page_ID, properties = None):
        created_page = self._notionExecutor(self.pages.update,**{'page_id': page_ID,
                       'properties': properties})
        return created_page.get('id')

    def retrieve_page(self, page_ID):
        return self._notionExecutor(
            self.pages.retrieve, **{'page_id': page_ID})

    def delete_page(self, page_ID):
        self._notionExecutor(
            self.blocks.delete, **{'block_id': page_ID})

    def retrieve_block(self, block_ID):
        return self._notionExecutor(
            self.blocks.retrieve, **{'block_id': block_ID})

    def retrieve_block_children_list(self, page_ID):
        return self._notionExecutor(
            self.blocks.children.list, **{'block_id': page_ID})

    def update_block(self, block_ID, field, field_value_updated):
        return self._notionExecutor(
            self.blocks.update, **{'block_id': block_ID, field: field_value_updated})

    def __row_hash(self, row):
        row_dict = row.to_dict()
        if self._ROW_HASH_KEY in row_dict:
            del row_dict[self._ROW_HASH_KEY]
        return self.__calculate_dict_hash(row_dict)

    def __calculate_dict_hash(self, d):
        serialized_dict = json.dumps(d, sort_keys=True)
        return hash(serialized_dict)

    def __get_database_columnsAndTypes(self, database_ID):
        columns = self.get_database_columns(database_ID)
        if columns is None:
            return None
        return list(map(lambda notion_property:
                        (columns.get('properties').get(notion_property).get('name'),
                         columns.get('properties').get(notion_property).get('type')),
                        columns.get('properties')))

    def from_notion_DB_to_dataframe(self, database_ID, filter_params={}):
        results = self._notionExecutor(
            collect_paginated_api,
            **{'function': self.databases.query, **filter_params, "database_id": database_ID})
        database_data = []
        for result in results:
            prop_dict = {}
            for notion_property in result.get("properties"):
                prop_dict[str(notion_property)] = self.__readValueFromNotion(
                    result.get("properties").get(notion_property))
            prop_dict[self._ROW_PAGEID_KEY] = result.get("id")
            database_data.append(prop_dict)
        df = pd.DataFrame(database_data)
        df[self._ROW_HASH_KEY] = df.apply(
            lambda row: self.__row_hash(row), axis=1)
        return df

    def update_notion_DB_from_dataframe(self, database_ID, df):
        columns = self.__get_database_columnsAndTypes(database_ID)
        for index, row in df.iterrows():
            if self.__row_hash(row) != row['Row_Hash']:
                prop_dict = {}
                for column in columns:
                    columnName = column[0]
                    columnType = column[1]
                    if (columnType in self.read_only_columns):
                        continue
                    prop_dict[columnName] = self.__writeValueToNotion(
                        row[columnName], columnType)
                if row[self._ROW_PAGEID_KEY] != '':
                    self.update_page(row[self._ROW_PAGEID_KEY], prop_dict)
                else:
                    self.create_page(database_ID, prop_dict)

    def __readValueFromNotion(self, notion_property):
        return self.__get_value_from_lambda(
            notion_property, notion_property.get("type"), 0)

    def __writeValueToNotion(self, row_value, notion_type):
        return self.__get_value_from_lambda(
            row_value, notion_type, 1)

    def __get_value_from_lambda(self, input_value, notion_type, lambda_index):
        switcher = {
            'title': self.title_read_write_lambdas[lambda_index],
            'rich_text': self.rich_text_read_write_lambdas[lambda_index],
            'checkbox': self.checkbox_read_write_lambdas[lambda_index],
            'created_time': self.created_time_read_write_lambdas[lambda_index],
            'number': self.number_read_write_lambdas[lambda_index],
            'email': self.email_read_write_lambdas[lambda_index],
            'url': self.url_read_write_lambdas[lambda_index],
            'multi_select': self.multi_select_read_write_lambdas[lambda_index],
            'select': self.select_read_write_lambdas[lambda_index],
            'date': self.date_read_write_lambdas[lambda_index],
            'files': self.files_read_write_lambdas[lambda_index],
            'formula': self.formula_read_write_lambdas[lambda_index],
            'phone_number': self.phone_number_read_write_lambdas[lambda_index],
            'status': self.status_read_write_lambdas[lambda_index],
            'unique_id': self.unique_id_read_write_lambdas[lambda_index],
            'created_by': self.created_by_read_write_lambdas[lambda_index],
            'last_edited_time': self.last_edited_time_read_write_lambdas[lambda_index],
            'string': self.string_read_write_lambdas[lambda_index],
            'last_edited_by': self.last_edited_by_read_write_lambdas[lambda_index],
            'button': self.button_read_write_lambdas[lambda_index],
            'relation': self.relation_read_write_lambdas[lambda_index],
            'rollup': self.rollup_read_write_lambdas[lambda_index],
            'people': self.people_read_write_lambdas[lambda_index]
        }

        return switcher.get(notion_type, lambda: "Invalid: " + input_value)(input_value)
