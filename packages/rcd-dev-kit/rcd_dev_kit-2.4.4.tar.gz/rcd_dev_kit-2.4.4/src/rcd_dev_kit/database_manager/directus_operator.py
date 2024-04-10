import json
from typing import Optional, List, Any
import requests
from datetime import date, timedelta, datetime
from dateutil import parser
import warnings
import re
import os
import time

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def upsert_dataset_dates(
        schema_name,
        table_name,
        last_update,
        start_period,
        end_period,
        **kwargs: Any,
):
    dt_last_update = parser.parse(last_update)
    last_update_date_format = '%Y-%m-%dT%H:%M:%S'

    # Some tables, like dictionaries, don't have start and end periods.
    if {start_period, end_period} == {""}:
        dt_start_period, dt_end_period = start_period, end_period
    else:
        # Parse into date
        dt_start_period = parser.parse(start_period)
        dt_end_period = parser.parse(end_period)

        # Reformat the date into the Directus accepted format
        period_date_format = '%d-%m-%Y'
        dt_start_period = dt_start_period.strftime(period_date_format)
        dt_end_period = dt_end_period.strftime(period_date_format)

    data = f"""{{ 
                last_update: "{dt_last_update.strftime(last_update_date_format)}",
                start_period: "{dt_start_period}",
                end_period: "{dt_end_period}",
                table_owner: "{os.getenv('REDSHIFT_USER')}"
            }}"""

    do = DirectusOperator()
    json_dataset = do.get_dataset_items_id(lst_tables=[table_name])

    if len(json_dataset["data"]["Dataset"]) > 0:
        print("Table already exists in Directus. Updating last_update, start_period and end_period...")
        dataset_id = json_dataset["data"]["Dataset"][0]["id"]
        do.update_assets_items(ids=[dataset_id], data=data)
        print("✅ Dataset updated successfully!")
    else:
        print("Table doesn't exist yet in Directus. Creating table in Directus and setting "
              "last_update, start_period and end_period...")
        status = kwargs.get("status", "draft")
        nickname = kwargs.get("nickname", "")
        do.create_dataset(
            status=status,
            nickname=nickname,
            schema_name=schema_name,
            table_name=table_name,
            last_update=dt_last_update.strftime(last_update_date_format),
            start_period=dt_start_period,
            end_period=dt_end_period,
            table_owner=os.getenv('REDSHIFT_USER'))
        print("✅ Dataset created successfully!")


def upsert_es_indices(
        index_name,
        index_id,
        last_update,
        index_creation_date,
        block: str = "NULL",
        **kwargs: Any,
):
    dt_last_update = parser.parse(last_update)
    last_update_date_format = '%Y-%m-%dT%H:%M:%S'

    data = f"""{{ 
                last_update: "{dt_last_update.strftime(last_update_date_format)}",
                table_owner: "{os.getenv('REDSHIFT_USER')}"
            }}"""

    do = DirectusOperator()
    json_es_indices = do.get_es_index_items_id(lst_index=[index_name])

    if len(json_es_indices["data"]["ElasticSearch_Indices"]) > 0:
        print("Index already exists in Directus. Updating last_update...")
        dataset_id = json_es_indices["data"]["ElasticSearch_Indices"][0]["id"]
        do.update_assets_items(ids=[dataset_id], data=data, assets_types='ElasticSearch_Indices')
        print("✅ Dataset updated successfully!")
    else:
        print("Index doesn't exist yet in Directus. Creating index in Directus and setting "
              "last_update and index_creation_date...")

        status = kwargs.get("status", "draft")
        nickname = kwargs.get("nickname", "")
        do.create_es_index(
            index_name=index_name,
            index_id=index_id,
            last_update=last_update,
            index_creation_date=index_creation_date,
            status=status,
            block=block,
            table_owner=os.getenv('REDSHIFT_USER'),
            nickname=nickname
        )
        print("✅ ES Index created successfully!")


class DirectusOperator:
    def __init__(self) -> None:
        self.directus_token = os.environ.get('DIRECTUS_TOKEN')
        self.directus_endpoint = os.environ.get('DIRECTUS_API_URL')
        self.headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {self.directus_token}"}

    def post_request(self, query):
        resp = requests.post(f"{self.directus_endpoint}/graphql", json={'query': query}, headers=self.headers)
        if resp.status_code != 200 or '{"errors":[' in resp.text:
            raise SyntaxError(json.dumps(json.loads(resp.text), indent=4))

        return json.loads(resp.text)

    def update_dataset_items(self, ids: List, data: str):
        warnings.warn("update_dataset_items is deprecated, please use update_assets_items instead", DeprecationWarning)
        self.update_assets_items(ids=ids, List=data)

    def update_assets_items(self, ids: List, data: str, assets_types: str = 'Dataset'):
        query_update_item = f"""mutation {{
                                    update_{assets_types}_items(ids: {json.dumps(ids)}, 
                                    data: {data}) {{
                                        id
                                    }}
                                }}
                                """
        self.post_request(query=query_update_item)

    def get_dataset_items_id(
            self,
            lst_status: Optional[List] = None,
            lst_tables: Optional[List] = None,
            updated_yesterday: bool = True
    ):
        if lst_status is None:
            lst_status = ['Verified']
        query_filter = self.define_filter(lst_status=lst_status, lst_tables=lst_tables,
                                          updated_yesterday=updated_yesterday)
        query = f"""query {{
                        Dataset (
                            limit: -1,
                            {query_filter}
                            ) {{
                            id
                            status
                            table_name
                            schema_name
                        }}
                    }}"""
        resp = self.post_request(query=query)
        return resp

    def get_es_index_items_id(
            self,
            lst_status: Optional[List] = None,
            lst_index: Optional[List] = None,
            updated_yesterday: bool = False
    ):
        if lst_status is None:
            lst_status = ['Verified']

        query_filter = self.define_filter(lst_status=lst_status, lst_assets=lst_index, assets_type='index_name',
                                          updated_yesterday=updated_yesterday)
        query = f"""query {{
                        ElasticSearch_Indices (
                            limit: -1,
                            {query_filter}
                            ) {{
                            nickname
                            status,
                            id,
                            last_update,
                            index_creation_date,
                            table_owner,
                        }}
                    }}"""
        resp = self.post_request(query=query)
        return resp

    def get_dataset_items(
            self,
            lst_status: Optional[List] = None,
            lst_tables: Optional[List] = None,
            updated_yesterday: bool = True
    ):
        if lst_status is None:
            lst_status = ['Verified']
        query_filter = self.define_filter(lst_status=lst_status, lst_assets=lst_tables,
                                          updated_yesterday=updated_yesterday)
        query = f"""query {{
                        Dataset (
                            limit: -1,
                            {query_filter}
                            ) {{
                            id
                            status
                            user_created {{
                                email
                            }}
                            date_created
                            user_updated {{
                                email
                            }}
                            date_updated
                            nickname
                            detailed_description
                            table_name
                            schema_name
                            location
                            short_description
                            geographical_scope
                            table_type
                            data_coverage
                            geographical_granularity
                            time_granularity
                            update_frequency
                            last_update
                            last_update_func {{
                                day,
                                month,
                                weekday,
                                year,
                            }} 
                            start_period
                            end_period
                            caveats
                            additional_info
                            update_process
                            import_format
                            import_separator
                            data_cov_pctg
                            data_topics_and_metrics
                            table_owner
                            applications_list{{
                                Oip_Application_app_uuid {{
                                    app_uuid
                                    app_name
                                    app_description
                                    app_link
                                }}
                            }}
                            sources_list {{ 
                                Source_source_uuid {{
                                    source_uuid
                                    source_name
                                    source_description
                                    source_link
                                }}
                            }}
                            Columns {{
                                column_id
                                label
                                order
                            }}
                            business_keywords
                        }}
                    }}"""

        self.post_request(query=query)

    def define_filter(
            self,
            lst_status: Optional[List] = None,
            lst_assets: Optional[List] = None,
            lst_tables: Optional[List] = None,
            assets_type: Optional[str] = 'table_name',
            updated_yesterday: bool = True
    ):
        """
            Define a filter query for retrieving data based on specified criteria.

            Parameters:
                lst_status (Optional[List]): A list of statuses to filter by.
                lst_assets (Optional[List]): A list of assets to filter by.
                lst_tables (Optional[List]): DEPRECATED - A list of tables to filter by.
                assets_type (Optional[str]): The type of assets to filter. Defaults to 'table_name'.
                                        Other possible values include 'index_name', 'id', etc.
                updated_yesterday (bool): Whether to filter data updated yesterday (default is True).

            Returns:
                str: Filter query string.
            """
        if lst_tables is not None:
            warnings.warn("lst_tables arguments is deprecated, please use lst_assets instead",
                          DeprecationWarning)
            lst_assets = lst_tables

        date_yesterday = date.today() - timedelta(1)

        lst_assets_filter = ', '.join(
            [f"""{{{assets_type}: {{_eq: "{table}"}}}}""" for table in lst_assets]) + ',' if lst_assets else ''

        date_filter = ""
        status_filter = ""
        if not lst_assets_filter:
            if lst_status is None:
                lst_status = ['Verified']
            status_filter = ', '.join([f"""{{status: {{_eq: "{st}"}}}}""" for st in lst_status]) + ','
            if updated_yesterday:
                date_filter = f"""{{
                                    date_created_func: {{
                                        day: {{_eq: "{date_yesterday.day}"}},
                                        month: {{_eq: "{date_yesterday.month}"}},
                                        year: {{_eq: "{date_yesterday.year}"}}
                                        }}
                                    }},
                                    {{
                                    date_updated_func: {{
                                        day: {{_eq: "{date_yesterday.day}"}},
                                        month: {{_eq: "{date_yesterday.month}"}},
                                        year: {{_eq: "{date_yesterday.year}"}}
                                        }}
                                    }}"""

        query_filter = f"""filter:{{
                                _and:[ 
                                    {{_or: [
                                        {status_filter}
                                    ]}}
                                    {{_or: [
                                        {lst_assets_filter}
                                        {date_filter}
                                    ]}}
                                ]
                            }}"""
        return query_filter

    def create_dataset(
            self,
            schema_name,
            table_name,
            last_update,
            start_period,
            end_period,
            table_owner,
            status,
            nickname: Optional[str] = None
    ):
        query = f"""mutation {{
        create_Dataset_items(
                data: {{ 
                    nickname: "{str(nickname or '')}"
                    status: "{status}",
                    table_name: "{table_name}",
                    schema_name: "{schema_name}",
                    last_update: "{last_update}",
                    start_period: "{start_period}",
                    end_period: "{end_period}",
                    table_owner: "{table_owner}"
                    }}) {{  
                id
                schema_name,
                table_name,
                status
                }}
        }}"""

        self.post_request(query=query)

    def create_es_index(
            self,
            index_name,
            index_id,
            last_update,
            index_creation_date,
            status,
            table_owner,
            block,
            nickname: Optional[str] = None
    ):
        query = f"""mutation {{
        create_ElasticSearch_Indices_items(
                data: {{ 
                    nickname: "{str(nickname or '')}"
                    status: "{status}",
                    index_name: "{index_name}",
                    id: "{index_id}",
                    block: "{block}",
                    last_update: "{last_update}",
                    index_creation_date: "{index_creation_date}",
                    table_owner: "{table_owner}"
                    }}) {{  
                nickname
                status,
                index_name,
                id,
                block,
                last_update,
                index_creation_date,
                table_owner,
                }}
        }}"""

        self.post_request(query=query)
