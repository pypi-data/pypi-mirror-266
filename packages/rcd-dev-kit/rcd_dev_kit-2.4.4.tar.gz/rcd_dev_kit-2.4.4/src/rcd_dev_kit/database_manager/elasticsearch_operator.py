import os
import re
import json
import certifi
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Generator, Optional
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch.helpers import parallel_bulk, bulk, scan
from .. import decorator_manager
from .directus_operator import upsert_es_indices
from tqdm import tqdm
import logging
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.vector_stores.elasticsearch import ElasticsearchStore
# from llama_index.core import (
#     VectorStoreIndex,
#     StorageContext,
#     Settings,
#     Document
# )
import sys
def index_json_bulk_parallel(index: str, method: str, custom_mapping_json: Optional[dict] = None,
                             **kwargs: Any) -> None:
    """
    Function index_json_bulk_parallel.
    Use this function to send data to elasticsearch with bulk indexing and multi-threading.

    Args:
        index(str): The name of index in elasticsearch.
        method (str): "json" send to elasticsearch with local .json file, or "dataframe" send to elasticsearch with pandas dataframe.
        custom_mapping_json (dict, None):
            Json value containing the index custom mapping.
            Obs: In Elasticsearch, mappings are used to define how documents and their fields are indexed and stored
                 in the search engine. When you index data into Elasticsearch, it automatically tries to infer the data
                 types of the fields based on the JSON documents you provide. However, you can also explicitly define
                 custom mappings to have more control over how the data is indexed and analyzed.
    Kwargs:
        keyword(str): Only for method="json", the keyword to filter json file. By default it is an empty string.
        json_path(str): Only for method="json", the local directory which contains json file.

        df(pd.Dataframe): Only for method="dataframe", pandas dataframe object to index.
    Examples:
        >>> from rcd_dev_kit import database_manager
        >>> database_manager.index_json_bulk_parallel(index="my_index", method="json", json_path="my_json_path", keyword="")
        >>> database_manager.index_json_bulk_parallel(index="my_index", method="dataframe", df=pd.DataFrame())
    """
    pytest = kwargs.get("pytest", False)

    eo = ElasticsearchOperator(index=index)
    request_timeout = kwargs.get("request_timeout", 1200)

    if custom_mapping_json:
        eo.mapping = custom_mapping_json
        eo.set_custom_mapping()

    if method == "json":
        eo.json_path = kwargs.get("json_path")
        eo.detect_json(keyword=kwargs.get("keyword"))
    elif method == "dataframe":
        eo.pd_dataframe = kwargs.get("df")
    else:
        raise ValueError(f"Unrecognized method: {method}")

    while True:
        try:
            eo.request_timeout = request_timeout
            eo.parallel_bulk_index()
            break
        except ConnectionTimeout:
            is_again = input(
                "Elasticsearch.exceptions.ConnectionTimeout Error... do you want to try again with request_timeout? (y or n)"
            )
            if is_again == "n":
                break
            while request_timeout <= 1200:
                request_timeout = int(
                    input("Enter your request_timeout setting: (integer > 1200)")
                )
            print(f"Restarting with time_out {request_timeout}.")
    
    host = os.environ.get("ELASTICSEARCH_HOST")
    if not "localhost" in host:
        send_metadata(es_connector=eo.connection, index=index, pytest=pytest)


def index_json_bulk(
        json_path: str, index: str, keyword: str = "", custom_mapping_json: Optional[dict] = None, **kwargs: Any
) -> None:
    """
    Function index_json_bulk.
    Use this function to send data to elasticsearch with bulk indexing.

    Args:
        json_path (str): The path of json directory.
        index(str): The name of index in elasticsearch.
        keyword(str): The keyword to filter json file. By default it is an empty string.
        custom_mapping_json (dict, None):
            Json value containing the index custom mapping.
            Obs: In Elasticsearch, mappings are used to define how documents and their fields are indexed and stored
                 in the search engine. When you index data into Elasticsearch, it automatically tries to infer the data
                 types of the fields based on the JSON documents you provide. However, you can also explicitly define
                 custom mappings to have more control over how the data is indexed and analyzed.
    Examples:
        >>> from rcd_dev_kit import database_manager
        >>> database_manager.index_json_bulk(index="my_index", json_path="my_json_path", keyword="")
    """
    eo = ElasticsearchOperator(index=index)
    eo.json_path = json_path
    eo.detect_json(keyword=keyword)
    request_timeout = kwargs.get("request_timeout", 1200)

    if custom_mapping_json:
        eo.mapping = custom_mapping_json
        eo.set_custom_mapping()

    while True:
        try:
            eo.request_timeout = request_timeout
            eo.bulk_index()
            break
        except ConnectionTimeout:
            is_again = input(
                "Elasticsearch.exceptions.ConnectionTimeout Error... do you want to try again with request_timeout? (y or n)"
            )
            if is_again == "n":
                break
            while request_timeout <= 1200:
                request_timeout = int(
                    input("Enter your request_timeout setting: (integer > 1200)")
                )
            print(f"Restarting with time_out {request_timeout}.")

    host = os.environ.get("ELASTICSEARCH_HOST")
    
    if not "localhost" in host:
        send_metadata(es_connector=eo.connection, index=False)


def index_json(
        json_path: str,
        index: str,
        keyword: str = "",
        show_debug: bool = True,
        custom_mapping_json: Optional[dict] = None,
        **kwargs: Any,
):
    """
    Function index_json.
    Use this function to send data to elasticsearch with normal indexing.

    Parameters:
          json_path (str): The path of json directory.
          index(str): The name of index in elasticsearch.
          keyword(str): The keyword to filter json file. By default it is an empty string.
          show_debug(bool): Display debugging information or not.
          custom_mapping_json (dict, None):
            Json value containing the index custom mapping.
            Obs: In Elasticsearch, mappings are used to define how documents and their fields are indexed and stored
                 in the search engine. When you index data into Elasticsearch, it automatically tries to infer the data
                 types of the fields based on the JSON documents you provide. However, you can also explicitly define
                 custom mappings to have more control over how the data is indexed and analyzed.
    Examples:
        >>> from rcd_dev_kit import database_manager
        >>> database_manager.index_json(json_path="my_json_path", index="my_index", keyword="")
    """
    eo = ElasticsearchOperator(index=index)
    eo.json_path = json_path
    eo.detect_json(keyword=keyword)
    if kwargs.get("request_timeout"):
        eo.request_timeout = kwargs.get("request_timeout")

    if custom_mapping_json:
        eo.mapping = custom_mapping_json
        eo.set_custom_mapping()

    eo.normal_index_json(show_debug=show_debug)
    host = os.environ.get("ELASTICSEARCH_HOST")
    if not "localhost" in host:
        send_metadata(es_connector=eo.connection, index=False)


def send_metadata(es_connector, index, **kwargs):
    pytest = kwargs.get("pytest", False)

    # Extract Creation Date
    resp_index_metadata = es_connector.indices.get(index=index)
    creation_timestamp = int(resp_index_metadata[index]["settings"]["index"]["creation_date"]) // 1000
    creation_datetime = datetime.utcfromtimestamp(creation_timestamp)

    block = None
    match = re.search(r"block(\d+)", index)
    if match:
        block = match.group(1)

    upsert_es_indices(
        index_name=index,
        index_id=index,
        last_update=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        index_creation_date=creation_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
        status=('Archived' if pytest else "Ingested"),
        nickname=('Generated by pyTest' if pytest else ""),
        block=(block if block is not None else "NULL")
    )


class ElasticsearchOperator:
    """
    Class ElasticsearchOperator.
    Use this class to manipulate data with elasticsearch.

    Parameters:
          index (str): elasticsearch index name.
    """

    def __init__(self, index: str) -> None:
        host = os.environ.get("ELASTICSEARCH_HOST")
        user = os.environ.get("ELASTICSEARCH_USER")
        password = os.environ.get("ELASTICSEARCH_PASSWORD")
        scheme = os.environ.get("ELASTICSEARCH_SCHEME")
        port = int(os.environ.get("ELASTICSEARCH_PORT"))

              # Check if the scheme is https when the host is not localhost for security reasons
        if "localhost" not in host and scheme != "https":
            raise ValueError("TLS options require scheme to be 'https' when not using localhost.")

        # Configure connection based on whether host is local or not
        if "localhost" in host:
            # Local environment: no authentication
            print(f"Local environment")
            self.connection = Elasticsearch(
                [
                    {'host': host, 'port': port, "scheme": scheme}
                ],
            )


        else:

            self.connection = Elasticsearch(
                [
                    {'host': host, 'port': port, "scheme": scheme}
                ],
                http_auth=(user, password),
                ca_certs=certifi.where(),
            )

        self._mapping = None
        self._json_path = None
        self._pd_dataframe = None
        self._request_timeout = 1200
        self.index = index
        self.lst_json = list()

    @property
    def json_path(self) -> str:
        return self._json_path

    @json_path.setter
    def json_path(self, path: str) -> None:
        print(f"Setting json_path to {path}")
        self._json_path = path

    @property
    def pd_dataframe(self) -> pd.DataFrame:
        return self._pd_dataframe

    @pd_dataframe.setter
    def pd_dataframe(self, df: pd.DataFrame) -> None:
        print(f"Reading df with shape {df.shape}")
        self._pd_dataframe = df

    @property
    def request_timeout(self) -> int:
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self, value: int) -> None:
        print(f"Setting request_timeout to {value}")
        self._request_timeout = value

    @property
    def mapping(self) -> dict:
        return self._mapping

    @mapping.setter
    def mapping(self, value: dict) -> None:
        print(f"Setting custom mapping json. 🖇")
        self._mapping = value

    def set_custom_mapping(self):
        """
        Set a custom mapping for the specified Elasticsearch index.

        This function creates or updates the mapping for the specified Elasticsearch index using
        the provided custom mapping definition. The `ignore=400` parameter is set to ignore
        index creation if the index already exists.

        Note:
        The `_mapping` parameter should be a valid Elasticsearch mapping definition in the form
        of a Python dictionary.

        Example:
        You can set a custom mapping for an Elasticsearch index with the following code:
        ```
        custom_mapping = {
            "properties": {
                "field1": {
                    "type": "text"
                },
                "field2": {
                    "type": "keyword"
                }
            }
        }

        your_instance.set_custom_mapping(custom_mapping)
        ```

        The `custom_mapping` dictionary defines the mapping for two fields, "field1" and "field2,"
        with their respective data types.

        """
        self.connection.indices.create(index=self.index, body=self._mapping, ignore=400)

    def detect_json(self, keyword: str) -> None:
        """
        Detect JSON files in the specified directory containing a keyword in their names.

        This function scans the directory for JSON files and filters those that both have the ".json"
        file extension and contain the specified keyword in their names.

        Args:
            keyword (str): The keyword to search for in the JSON file names.

        Example:
        If `json_path` is a directory containing the following files:
        - data_file.json
        - report.json
        - document_data.json
        - metadata.json

        Calling `detect_json("data")` would detect and populate `self.lst_json` with:
        ['data_file.json', 'document_data.json']

        The function would print "2 .json files with keyword 'data' detected."

        """
        self.lst_json = [
            file
            for file in os.listdir(self.json_path)
            if (file.endswith(".json"))
               and (not file.startswith("."))
               and (keyword in file)
        ]
        print(f"{len(self.lst_json)} .json files with keyword '{keyword}' detected.")

    def index_json(self, json_file: str, show_debug: bool = True) -> None:
        """
        Index a JSON document into Elasticsearch.

        This function indexes a JSON document from a file into the specified Elasticsearch index.
        Optionally, it can print a debug message after indexing.

        Args:
            json_file (str): The name of the JSON file to index.
            show_debug (bool, optional): Whether to print a debug message after indexing.
                Defaults to True.

        Raises:
            FileNotFoundError: If the specified JSON file is not found.
        """
        document_id = json_file.rsplit(".json")[0]
        json_file_path = os.path.join(self.json_path, json_file)

        if not os.path.isfile(json_file_path):
            raise FileNotFoundError(f"JSON file '{json_file}' not found.")

        with open(json_file_path) as f:
            reader = json.load(f)
            reader["@timestamp"] = str(datetime.now())
            publish = self.connection.index(
                index=self.index,
                doc_type="_doc",
                id=document_id,
                body=reader,
                request_timeout=self._request_timeout,
            )
            if show_debug:
                print(f"Doc with id {publish['_id']} is published.")

    @decorator_manager.timeit(program_name="Normal indexing")
    def normal_index_json(self, show_debug: bool = False) -> None:
        """
        Method normal_index_json, which calls self.index_json method.
        Use this method to index json data to elasticsearch.

        Parameters:
              show_debug (bool): Display debug information or not. By default it is True.
        """
        for json_file in self.lst_json:
            self.index_json(json_file=json_file, show_debug=show_debug)

    def json_generator(self) -> Generator:
        """
        Generate actions for bulk indexing data from JSON files into Elasticsearch.

        This function reads JSON files from a specified directory and generates actions
        for indexing the content of those files into Elasticsearch.

        Yields:
            dict: A dictionary containing the action to index data into Elasticsearch.

        Example action:
        {
            "_id": <document_id>,
            "_source": <document_content>,
            "_index": <Elasticsearch_index_name>
        }
        """
        for json_file in self.lst_json:
            with open(os.path.join(self.json_path, json_file)) as f:
                d = json.load(f)
                d["@timestamp"] = str(datetime.now())
                yield {
                    "_id": json_file.split(".json")[0],
                    "_source": d,
                    "_index": self.index,
                }

    def df_generator(self) -> Generator:
        """
        Generate actions for bulk indexing data from a pandas DataFrame into Elasticsearch.

        This function converts the pandas DataFrame into a JSON representation and generates
        actions for indexing data into Elasticsearch.

        Yields:
            dict: A dictionary containing the action to index data into Elasticsearch.

        Example action:
        {
            "_id": <document_id>,
            "_source": <document_content>,
            "_index": <Elasticsearch_index_name>
        }
        """
        str_json = self.pd_dataframe.to_json(orient="records", force_ascii=False)
        lst_json = json.loads(str_json)
        for json_id, json_content in zip(self.pd_dataframe.index, lst_json):
            # Add a timestamp to the JSON content.
            json_content["@timestamp"] = str(datetime.now())
            yield {"_id": json_id, "_source": json_content, "_index": self.index}

    def get_generator(self) -> Generator:
        """
        Get a generator for indexing data into Elasticsearch.

        This function checks the data sources (lst_json and pd_dataframe) and returns an appropriate
        generator for bulk indexing based on the available data source.

        Returns:
            Generator: A generator for indexing data into Elasticsearch.

        Raises:
            ValueError: If neither lst_json nor pd_dataframe is defined.
        """
        if len(self.lst_json) != 0:
            print("Index by JSON files")
            return self.json_generator()
        elif not self.pd_dataframe.empty:
            print("Index by pandas DataFrame")
            return self.df_generator()
        else:
            raise ValueError("Define at least one of the following: lst_json or pd_dataframe")

    @decorator_manager.timeit(program_name="Bulk indexing")
    def bulk_index(self) -> None:
        """
        Perform bulk indexing of actions into Elasticsearch.

        This function uses the Elasticsearch bulk method to index a batch of actions into Elasticsearch.
        It doesn't handle errors here; you should use the `bulk()` method in a try-except block to
        catch and handle any indexing errors.
        """
        bulk(
            client=self.connection,
            actions=self.get_generator(),  # This should return a generator of actions.
            request_timeout=self._request_timeout,
        )

    @decorator_manager.timeit(program_name="Parallel Bulk indexing")
    def parallel_bulk_index(self) -> None:
        """
        Perform parallel bulk indexing of actions into Elasticsearch and handle errors.

        This function uses the Elasticsearch parallel_bulk method to index a batch of actions into
        Elasticsearch in parallel. It iterates through the results of the bulk indexing and
        prints error information if any indexing operation is unsuccessful.
        """
        for success, info in parallel_bulk(
                client=self.connection,
                actions=self.get_generator(),  # This should return a generator of actions.
                request_timeout=self._request_timeout,
        ):
            if not success:
                # Print error information for unsuccessful indexing operations.
                print(info)

    # disabling to avoid dependency on llama_index which is not stable enough
    # @decorator_manager.timeit(program_name="Create a vector store")
    # def generate_vector_store(self, df:pd.DataFrame, index_name:str, field_concat_for_embedding:list[str], metadata_fields:list[str], model_name="NeuML/pubmedbert-base-embeddings"):
    #     """
    #     Creates a vector store by generating embeddings for each document in the provided DataFrame and indexing these documents into an Elasticsearch vector store.

    #     This method processes the DataFrame by concatenating specified fields to create a text for each document, attaching specified metadata, generating embeddings using the SentenceTransformer library based on the concatenated text, and finally indexing these documents into Elasticsearch.

    #     Parameters:
    #     - df (pd.DataFrame): The DataFrame containing the data to be processed. Each row represents a document.
    #     - index (str): The base name for the Elasticsearch index where the documents will be stored. The final index name will be '{index}_vstore'.
    #     - field_concat_for_embedding (list of str): Fields from the DataFrame to be concatenated to form the text content of each document.
    #     - metadata_fields (list of str): Fields from the DataFrame to be included as metadata for each document.
    #     - model_name (str, optional): The model name to be used with the SentenceTransformer for generating embeddings. Defaults to "NeuML/pubmedbert-base-embeddings".

    #     The method also uses class attributes for Elasticsearch connection details (host, user, password) to determine whether to connect to a local or remote Elasticsearch instance.

    #     The generated vector store can be used for searching, similarity comparisons, and other vector-based operations supported by Elasticsearch.
    #     """
    #     documents = []
        
    #     # Iterate through DataFrame rows with a progress bar
    #     for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Generating documents"):
    #         # Create text by concatenating specified fields
    #         text = ' '.join([str(row[field]) for field in field_concat_for_embedding])
            
    #         # Prepare metadata using specified fields
    #         metadata = {field: row[field] for field in metadata_fields if not (isinstance(row[field], (list, np.ndarray)) and not row[field])}
    #         for field in metadata_fields:
    #             try:
    #                 if pd.notnull(row[field]):
    #                     # This line is just for debugging; remove or replace with appropriate handling
    #                     # print(f"Field {field} is not null.")
    #                     pass  # Add an indented block here
    #             except ValueError as e:
    #                 print(f"Error with field {field}: {e}")



            
    #         # Create Document with text and metadata
    #         document = Document(text=text, metadata=metadata)
    #         documents.append(document)

    #     Settings.embed_model = HuggingFaceEmbedding(
    #          model_name=model_name
    #     )
    #     host = os.environ.get("ELASTICSEARCH_HOST")
    #     user = os.environ.get("ELASTICSEARCH_USER")
    #     password = os.environ.get("ELASTICSEARCH_PASSWORD")
    #     scheme = os.environ.get("ELASTICSEARCH_SCHEME")
    #     port = int(os.environ.get("ELASTICSEARCH_PORT"))
    #     url = scheme+'://'+host+':'+str(port)
    #     print(url)

    #     if not "localhost" in host:
    #         vector_store = ElasticsearchStore(
    #             es_url=url,
    #             es_user=user,
    #             es_password=password,
    #             index_name=index_name+'_vstore',
    #         )
    #     else: 
    #         vector_store = ElasticsearchStore(
    #             es_url=url,
    #             index_name=index_name+'_vstore',
    #         )

    #     storage_context = StorageContext.from_defaults(vector_store=vector_store)
    #     print(documents[0])
    #     index = VectorStoreIndex.from_documents(
    #         documents, storage_context=storage_context
    #     )

    #     # if not "localhost" in self.host:
    #     #     send_metadata(es_connector=self.connection, index=False)


    @decorator_manager.timeit(program_name="Dropping Index")
    def delete_index(self):
        self.connection.indices.delete(index=self.index, ignore=[400, 404])


    @decorator_manager.timeit(program_name="Dropping Index")
    def index_to_df(self, scroll: str = "1m") -> pd.DataFrame:
        """
        Retrieve data from an Elasticsearch index and convert it to a pandas DataFrame.

        Args:
            scroll (str, optional): The time duration for scroll search (e.g., "1m" for 1 minute).
                Defaults to "1m".

        Returns:
            pd.DataFrame: A DataFrame containing the data from the Elasticsearch index.
        """
        # Define the Elasticsearch query to match all documents.
        query = {
            "query": {
                "match_all": {}
            }
        }

        # Use the Elasticsearch scan function to retrieve data from the index.
        elasticsearch_data = scan(
            client=self.connection,
            query=query,
            scroll=scroll,
            index=self.index,
            raise_on_error=True,
            preserve_order=False,
            clear_scroll=True
        )

        # Convert the Elasticsearch results into a list.
        lst_result = list(elasticsearch_data)

        # Extract the '_source' field from each hit and store it in a list.
        lst_index_dimensions = []
        for hit in lst_result:
            lst_index_dimensions.append(hit['_source'])

        # Convert the list of '_source' data into a pandas DataFrame.
        return pd.DataFrame(lst_index_dimensions)
