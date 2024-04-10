from snowflake.connector.pandas_tools import write_pandas
from typing import List, Optional, Any
import snowflake.connector
from tqdm import tqdm
import pandas as pd
import sqlparse
import time
import os
import re
from ..sql_utils import convert_to_snowflake_syntax, correct_sql_system_variables_syntax
from ..pandas_manager import check_quality_table_names
from .redshift_operator import RedshiftOperator
from .s3_operator import S3Operator


def send_to_snowflake(
        database: str,
        schema: str,
        table: str,
        df: pd.DataFrame,
        send_to_s3: bool = False,
        **kwargs: Any
):
    """
    Use this function to send a DataFrame to Snowflake.

    :param database: The database name.
    :param schema: The schema name.
    :param table: The table name.
    :param df: The Dataframe.
    :param send_to_s3: Boolan value to indicate if the function should send the object as well to S3.
    :param kwargs: Extra arguments as 'bucket' with the bucket name.

    :return: None
    """
    # Check if the column names agree with the SQL standards. It must not have accented letters or any special
    # character.
    check_quality_table_names(table_name=table, df=df)

    if send_to_s3:
        so = S3Operator()
        if database.lower() == 'oip':
            so.bucket = kwargs.get("bucket", os.environ.get("S3_BUCKET_DATAMART"))
            raise ValueError("❌ Environment variable missing: S3_BUCKET_DATAMART")
        else:
            so.bucket = kwargs.get("bucket", os.environ.get("S3_BUCKET_DEV"))
            if so.bucket is None:
                raise ValueError("❌ Environment variable missing: S3_BUCKET_DEV")

        so.send_to_s3_obj(df=df, s3_file_path=os.path.join(schema, f"{table}.csv"), sep="|")

    sf = SnowflakeOperator(snowflake_database=database)
    sf.schema = schema
    sf.send_table(df=df, table_name=table)
    sf.conn.close()


def read_from_snowflake(database: str, schema: str, table: str) -> pd.DataFrame:
    """
    Use this function to read data from Snowflake.

    :param database: The database name.
    :param schema: The schema name.
    :param table: The table name.

    :return: Table from Snowflake in pd.Dataframe format.
    """
    sf = SnowflakeOperator(snowflake_database=database)
    sf.schema = schema
    df = sf.get_table(table_name=table)
    sf.conn.close()

    return df


def migrate_data_from_redshift(
        rs_db: str,
        sf_db: str,
        schemas_list: Optional[List[str]] = None,
        avoid_schemas_list: Optional[List[str]] = None,
        tables_list: Optional[List[str]] = None,
        avoid_tables_list: Optional[List[str]] = None,
        avoid_materialized_views: bool = True,
        big_data_table_names: Optional[List[str]] = None,
        logging: bool = True,
        verbose: bool = True,
        schema_migration_dict: Optional[dict] = None,
        drop_old_tables: bool = True
) -> List[str]:
    """
    Launches a Data Migration process sending tables from Redshift into Snowflake.

    Args:
        rs_db (str): Redshift database name.
        sf_db (str): Snowflake database name.
        schemas_list (List[str], optional): List of schemas to be migrated.
        avoid_schemas_list (List[str], optional): List of schemas to be avoided.
        tables_list (List[str], optional): List of tables to be migrated.
        avoid_tables_list (List[str], optional): List of tables to be avoided.
        avoid_materialized_views (bool, optional): To avoid Materialized View Tables to be migrated. Default is True.
        big_data_table_names (List[str], optional): List of names for the Big Data Tables.
        logging (bool, optional): If True, creates a query_log_errors.txt listing all problematic queries. Default is True.
        verbose (bool, optional): If True, sets exhaustive printing. Default is True.
        schema_migration_dict (dict, optional): Dictionary for schema migration. Example:
            {"schema1": "schema2"} to migrate data from schema1 in Redshift to schema2 in Snowflake.
        drop_old_tables (bool, optional): If True, drops old tables in Snowflake before migrating. Default is True.

    Returns:
        List: Two values - 1st: a string with the amount of time it took to process everything.
          2nd: a list with the schema, table name, and error encountered (if any) when migrating.
    """
    ro = RedshiftOperator(database=rs_db)
    ddl_df = ro.get_DDL(
        schema_names=schemas_list,
        avoid_schema_names=avoid_schemas_list,
        table_names=tables_list,
        avoid_table_names=avoid_tables_list,
        verbose=verbose
    )
    ddl_df.fillna("", inplace=True)

    if big_data_table_names is None:
        big_data_table_names = []
    if schema_migration_dict:
        ddl_df.replace(schema_migration_dict, regex=True, inplace=True)
    if avoid_materialized_views:
        ddl_df = ddl_df[~ddl_df.table_name.str.contains('^mv_')]
    if logging:
        if os.path.exists("query_log_errors.txt"):
            os.remove("query_log_errors.txt")

    print("🦆 Migrating Redshift into Snowflake:")
    all_times_list, error_tables = [], []
    if ddl_df.__len__() > 0:
        sf = SnowflakeOperator(snowflake_database=sf_db)
        string_check = re.compile("[\s@\-!#$%^&*+()<>?/\|}{~:]")  # Regex to find special characters.
        with tqdm(total=ddl_df.__len__(), ncols=150, dynamic_ncols=True) as pb:
            for index, row in ddl_df.iterrows():
                try:
                    redshift_schema = row['schema_name']
                    table_name = row['table_name']

                    # Progression bar description.
                    pb.set_description(f"Processing... --> {redshift_schema} | {table_name} ")

                    # Checking for table names with non-standard names. In that case, quotes must be added.
                    if not table_name.isascii() or (string_check.search(table_name) is not None):
                        table_name = f'"{table_name}"'

                    # Retrieving table from redshift as a Pandas Dataframe.
                    rs_start = time.time()
                    ro._schema = redshift_schema
                    ro._table = table_name
                    if table_name not in big_data_table_names:
                        df_from_redshift = ro.read_from_redshift()
                    else:
                        ro.unload_to_s3(
                            bucket=os.environ.get("S3_BUCKET_DATAMART"),
                            prefix=os.path.join("migrate_parquet_to_snowflake_temp/", redshift_schema)
                        )
                        df_from_redshift = ro.read_from_redshift(method="pandas", limit=1)
                        col_names_list = list(df_from_redshift.columns)
                    rs_time = time.time() - rs_start

                    # It should send to snowflake only if the table isn't empty.
                    if df_from_redshift.__len__() > 0:

                        # If any of the column names are non-standard as well quotes must be added. Also, in  Snowflake,
                        # the names 'values' and 'group' must have quotes as well since they are system variables.
                        for col_name in df_from_redshift.columns:
                            if (not col_name.isascii()
                                    or (string_check.search(col_name) is not None)
                                    or (col_name == "values") or (col_name == "group")):
                                df_from_redshift.rename(columns={col_name: f'"{col_name}"'}, inplace=True)

                        # Retrieving table from redshift as a Pandas Dataframe.
                        sf_start = time.time()
                        sf.schema = redshift_schema
                        if table_name not in big_data_table_names:
                            sf.send_table(df=df_from_redshift, table_name=table_name)
                        else:
                            sf.create_parquet_stage(
                                prefix="migrate_parquet_to_snowflake_temp",
                                table=table_name,
                                staging_name='aws_big_data_parquet'
                            )
                            sf.create_parquet_file_format(file_format_name="parquet_format")
                            sf.create_table_from_template(
                                table=table_name,
                                staging_name='aws_big_data_parquet',
                                file_format_name='parquet_format'
                            )
                            sf.copy_into(
                                table=table_name,
                                col_names=col_names_list,
                                staging_name='aws_big_data_parquet',
                                pattern=".*.parquet"
                            )
                        sf_time = time.time() - sf_start

                        all_times_list.append(rs_time + sf_time)
                except Exception as e:
                    error_tables.append([redshift_schema, table_name, str(e)])
                finally:
                    time.sleep(0.5)
                    pb.update(1)

        if drop_old_tables and not tables_list:
            # If the user has provided a specific list of tables to be transferred,
            # dropping old tables is unnecessary.
            # When the user selects a list of tables, the goal is not to synchronize everything
            # and then drop tables present in Snowflake but no longer in Redshift.
            # Instead, the intention is to transfer only the requested tables without dropping them.
            # However, if no tables_list was provided, it implies the user wants to synchronize
            # both data warehouses, adding missing tables and dropping deprecated tables.
            print("✂️ Checking for tables to drop in case they are no more in Redshift.")
            sf.drop_old_tables(ddl_df=ddl_df)

        # Closing all connections before passing to metadata migration. It's important to avoid any connections overflow.
        ro.conn.close()
        sf.conn.cursor().close()
        sf.conn.close()

        # Checking for errors when migrating tables.
        if len(error_tables):
            print("‼️ When migrating the tables into Snowflake, the following tables present some problems:")
            for error in error_tables:
                print(f" - {error[0]} | {error[1]}")
                print(f" ---> \t{error[2]}")

        meta_start = time.time()
        recreate_metadata_on_snowflake(
            sf_db,
            ddl_table=ddl_df,
            create_tables=False,
            logging=True
        )
        all_times_list.append(time.time() - meta_start)
        entire_processing_duration = round(sum(all_times_list), 2)
    else:
        entire_processing_duration = 0

    return [f"Execution Time: {entire_processing_duration}s", error_tables]


def migrate_metadata_from_redshift(
        rs_db: str,
        sf_db: str,
        schemas_list: Optional[List] = None,
        avoid_schemas_list: Optional[List[str]] = None,
        tables_list: Optional[List] = None,
        avoid_tables_list: Optional[List[str]] = None,
        create_tables: bool = False,
        logging: bool = True,
        verbose: bool = True,
        schema_migration_dict: Optional[dict] = None
) -> None:
    """
    Migrates metadata from Redshift to Snowflake.

    Args:
        rs_db (str): Redshift database name.
        sf_db (str): Snowflake database name.
        schemas_list (List[str], optional): List of schemas to be migrated.
        avoid_schemas_list (List[str], optional): List of schemas not to be included.
        tables_list (List[str], optional): List of tables to be migrated.
        avoid_tables_list (List[str], optional): List of tables not to be included.
        create_tables (bool, optional): If True, creates tables if they don't exist beforehand.
        logging (bool, optional): If True, logs problematic queries into query_log_errors.txt.
        verbose (bool, optional): If True, shows all DDL queries being read from Redshift tables.
        schema_migration_dict (dict, optional): Dictionary for schema migration. Example:
            {"schema1": "schema2"} to migrate metadata from schema1 in Redshift to schema2 in Snowflake.

    Returns:
        None
    """
    print("🦆 Starting the metadata migration process | Redshift -> Snowflake")

    # Connect to Redshift and retrieve DDL information
    ro = RedshiftOperator(database=rs_db)
    ddl_df = ro.get_DDL(
        schema_names=schemas_list,
        avoid_schema_names=avoid_schemas_list,
        table_names=tables_list,
        avoid_table_names=avoid_tables_list,
        verbose=verbose
    )
    ddl_df.fillna("", inplace=True)

    # Replace schema names if schema_migration_dict is provided
    if schema_migration_dict is not None:
        ddl_df.replace(
            schema_migration_dict,
            regex=True,
            inplace=True
        )

    # Clear the query log errors file if logging is enabled
    if logging:
        if os.path.exists("query_log_errors.txt"):
            os.remove("query_log_errors.txt")

    # Recreate metadata on Snowflake
    recreate_metadata_on_snowflake(
        sf_db,
        ddl_table=ddl_df,
        create_tables=create_tables,
        logging=True
    )


def recreate_metadata_on_snowflake(
        database: str,
        ddl_table: pd.DataFrame,
        create_tables: bool = False,
        logging: bool = True
) -> None:
    """
    Recreates metadata in Snowflake based on a ddl_table containing all the metadata information.

    Args:
        database (str): Snowflake database name.
        ddl_table (pd.DataFrame): DataFrame containing metadata information obtained from the Redshift Operator.
        create_tables (bool, optional): If True, creates tables if they don't already exist. Default is False.
        logging (bool, optional): If True, logs problematic queries in a query_log_errors.txt file. Default is True.

    Returns:
        None
    """
    print("💎 Launching Metadata Migration...\n")
    sf = SnowflakeOperator(snowflake_database=database.upper())
    ddl_model = ddl_table.copy()
    if create_tables:
        print("🖼 Creating tables if they don't already exist...")
        # Some of these corrections below must be done because 'year', 'level', 'region', 'names' are SQL Syntax Names
        # and AWS parse them as strings when creating the column names. However, Snowflake parses it otherwise because
        # it can distinguish the column names and the SQL Variables as different things.
        ddl_model['create_query'] = ddl_model['create_query'].str.replace("CREATE TABLE IF NOT EXISTS",
                                                                          "CREATE OR REPLACE TABLE")
        ddl_model["create_query"] = correct_sql_system_variables_syntax(ddl_model, "create_query")
        sf.execute_metadata_query(ddl_model.create_query.values, logging=logging, correct_syntax=True)

    print("🏷 Migrating Table Descriptions...")
    sf.execute_metadata_query(ddl_model.table_description.values, logging=logging)

    print("🏷 Migrating Columns Descriptions...")
    ddl_model["columns_description"] = correct_sql_system_variables_syntax(ddl_model, "columns_description")
    sf.execute_metadata_query(ddl_model.columns_description.values, logging=logging)

    print("🔑 Migrating Primary Keys...")
    sf.execute_key_query(ddl_model, key="primary", logging=logging)

    print("🔑 Migrating Unique Keys...")
    sf.execute_key_query(ddl_model, key="unique", logging=logging)

    print("🔑 Migrating Foreign Keys...")
    sf.execute_metadata_query(ddl_model.foreign_keys.values, logging=logging)

    sf.conn.cursor().close()
    sf.conn.close()
    print("✅ All metadata have been migrated successfully!")


class SnowflakeOperator:
    def __init__(
            self,
            snowflake_user: Optional[str] = None,
            snowflake_password: Optional[str] = None,
            snowflake_account: Optional[str] = None,
            snowflake_warehouse: Optional[str] = None,
            snowflake_role: Optional[str] = None,
            snowflake_database: Optional[str] = None
    ) -> None:
        """
        Initializes a SnowflakeOperator instance.

        Args:
            snowflake_user (str, optional): Snowflake username.
            snowflake_password (str, optional): Snowflake password.
            snowflake_account (str, optional): Snowflake account name.
            snowflake_warehouse (str, optional): Snowflake warehouse name.
            snowflake_role (str, optional): Snowflake role name.
            snowflake_database (str, optional): Snowflake database name.
        """

        self.snowflake_user = (
            os.environ.get("SNOWFLAKE_USER").upper()
            if snowflake_user is None
            else snowflake_user.upper()
        )
        self.snowflake_password = (
            os.environ.get("SNOWFLAKE_PASSWORD")
            if snowflake_password is None
            else snowflake_password
        )
        self.snowflake_account = (
            os.environ.get("SNOWFLAKE_ACCOUNT").upper()
            if snowflake_account is None
            else snowflake_account.upper()
        )
        self.snowflake_warehouse = (
            os.environ.get("SNOWFLAKE_WAREHOUSE").upper()
            if snowflake_warehouse is None
            else snowflake_warehouse.upper()
        )
        self.snowflake_role = (
            os.environ.get("SNOWFLAKE_ROLE").upper()
            if snowflake_role is None
            else snowflake_role.upper()
        )
        self.snowflake_database = (
            os.environ.get("SNOWFLAKE_DATABASE").upper()
            if snowflake_database is None
            else snowflake_database.upper()
        )

        self._schema = None

        self.conn = snowflake.connector.connect(
            user=self.snowflake_user,
            password=self.snowflake_password,
            account=self.snowflake_account,
            warehouse=self.snowflake_warehouse,
            role=self.snowflake_role,
            database=self.snowflake_database
        )

    @property
    def schema(self) -> str:
        return self._schema

    @schema.setter
    def schema(self, schema: str) -> None:
        self.conn.cursor().execute(f"USE SCHEMA {schema.upper()};")
        self._schema = schema

    def truncate(self, database, schema, table):
        sql = f"truncate table {database}.{schema}.{table};"
        self.conn.cursor().execute(sql)

    def drop_table(self, table: str, schema: Optional[str] = None):
        schema_name = self.schema.upper() if not schema else schema.upper()
        self.conn.cursor().execute(f"DROP TABLE IF EXISTS {schema_name}.{table.upper()};")

    def send_table(
            self,
            df: pd.DataFrame,
            table_name: str,
            quotes: bool = False,
            overwrite: bool = True
    ) -> None:
        """
        Sends a DataFrame to a Snowflake table.

        Args:
            df (pd.DataFrame): The DataFrame to be sent to Snowflake.
            table_name (str): The name of the Snowflake table to send the DataFrame to.
            quotes (bool, optional): If True, adds double quotes around identifiers. Default is False.
            overwrite (bool, optional): If True, overwrites the existing table. Default is True.

        Returns:
            None

        Raises:
            ValueError: If the schema name is not set.

        Example:
            instance.send_table(df=my_dataframe, table_name="example_table", quotes=True, overwrite=True)
        """
        # Use the specified Snowflake database
        self.conn.cursor().execute(f"USE DATABASE {self.snowflake_database.upper()};")

        # Drop the table if overwrite is True
        if overwrite:
            self.drop_table(table=table_name)

        # Determine the number of processor cores available on the computer
        processor_cores = os.cpu_count()
        # Subtract 2 from all available cores to parallelize the processing; can't be lower than 4.
        cores_usage = processor_cores - 2 if processor_cores >= 6 else processor_cores
        # Set a chunk size based on the size of the table
        chunk_usage = None if df.__len__() < 5 * 10 ** 6 else int(df.__len__() / 3)

        if self.schema is None:
            raise ValueError("❌ Please, set a schema name to where the table should be sent: \n"
                             "\t\t Example: sf = SnowflakeOperator()\n"
                             "\t\t          sf.schema = 'schema_name'")
        else:
            # Write the DataFrame to Snowflake using parallel processing
            success, nchunks, nrows, _ = write_pandas(
                conn=self.conn,
                df=df,
                table_name=table_name.upper(),
                schema=self.schema.upper(),
                database=self.snowflake_database.upper(),
                auto_create_table=True,
                # overwrite=True,
                chunk_size=chunk_usage,
                quote_identifiers=quotes,
                parallel=cores_usage
            )

    def get_table(self, table_name: str) -> pd.DataFrame:
        """
        Retrieves data from a Snowflake table and returns it as a DataFrame.

        Args:
            table_name (str): The name of the Snowflake table to retrieve data from.

        Returns:
            pd.DataFrame: Dataframe containing the retrieved data.

        Raises:
            ValueError: If the schema name is not set.

        Example:
            result_df = instance.get_table(table_name="example_table")
        """
        if self.schema is None:
            raise ValueError("❌ Please, set a schema name to where the table should be sent: \n"
                             "\t\t Example: sf = SnowflakeOperator()\n"
                             "\t\t          sf.schema = 'schema_name'")
        else:
            # Execute the Snowflake query to retrieve data from the specified table
            df_from_sf = self.conn.cursor().execute(
                f"SELECT * FROM {self.schema.upper()}.{table_name.upper()}"
            ).fetch_pandas_all()

        return df_from_sf

    def drop_old_tables(self, ddl_df: pd.DataFrame, schema_list: Optional[List[str]] = None) -> None:
        """
        Synchronizes tables in Snowflake and Redshift by dropping tables present in Snowflake but not in Redshift.

        Args:
            ddl_df (pd.DataFrame): DDL table listing all the tables with their schemas in Redshift.
            schema_list (List[str], optional): Subset of schemas under the DDL dataframe. Default is None.

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.drop_old_tables(ddl_df=redshift_ddl_df, schema_list=["schema1", "schema2"])
        """
        # Regex to find special characters
        string_check = re.compile("[\s@\-!#$%^&*+()<>?/\|}{~:]")  # Regex to find special characters.

        if schema_list:
            # Filter Snowflake tables based on provided schema_list
            df__sf_tables = self.list_tables(schema_list=schema_list)
            ddl_df = ddl_df[ddl_df.schema_name.isin(schema_list)]
        else:
            # Use all schemas from ddl_df if schema_list is not provided
            schema_list = list(ddl_df["schema_name"].unique())
            df__sf_tables = self.list_tables(schema_list=schema_list)

        for schema in schema_list:
            # Get lists of tables in Snowflake and Redshift for the current schema
            sf_tables_list = df__sf_tables.loc[df__sf_tables['TABLE_SCHEMA'] == schema.upper(),
                                               'TABLE_NAME'].str.lower().values
            rs_tables_list = ddl_df.loc[ddl_df['schema_name'] == schema, 'table_name'].values

            # Find tables in Snowflake but not in Redshift
            tables_to_drop_list = list(set(sf_tables_list) - set(rs_tables_list))

            if tables_to_drop_list:
                print(f"Schema: {schema}")
                for table in tables_to_drop_list:
                    # Handle special characters and non-ASCII characters in table names
                    if not table.isascii() or (string_check.search(table) is not None):
                        table = f'"{table}"'
                    print(f"\t🗑 Dropping table {schema.upper()}.{table.upper()}...")
                    # Call the drop_table method to drop the table in Snowflake
                    self.drop_table(schema=schema.upper(), table=table.upper())
            else:
                print(f"👌 There's no tables to drop in {schema}.")

    def list_tables(self, schema_list: List[str]) -> pd.DataFrame:
        """
        Lists all the tables in Snowflake for a set of schemas.

        Args:
            schema_list (List[str]): List of schemas from where it will list the tables.

        Returns:
            pd.DataFrame: Dataframe returned by the listing query.

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            result_df = instance.list_tables(schema_list=["schema1", "schema2"])
        """
        # Convert schema names to uppercase and create the WHERE clause
        schema_list = [f"TABLE_SCHEMA = '{schema.upper()}'" for schema in schema_list]
        schema_list = ' OR '.join(schema_list)

        # Execute the Snowflake query to list tables
        df_from_sf = self.conn.cursor().execute(
            f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE {schema_list} ;"
        ).fetch_pandas_all()

        # Return a subset of the dataframe with relevant columns
        return df_from_sf[["TABLE_SCHEMA", "TABLE_NAME"]]

    def copy_from_s3(
            self,
            s3_prefix: str,
            s3_file: str,
            schema: str,
            table: str,
            quotes: bool = False,
            sep: str = "|",
            empty_field_as_null: bool = True,
            null_if: List[str] = [""]
    ) -> None:
        """
        Copies data from an S3 location into a Snowflake table.

        Args:
            s3_prefix (str): Object prefix in S3.
            s3_file (str): Table name in S3.
            schema (str): Schema name in Snowflake.
            table (str): Table name in Snowflake.
            quotes (bool, optional): If True, adds double quotes around the table name. Default is False.
            sep (str, optional): Field delimiter for the data. Default is "|".
            empty_field_as_null (bool, optional): If True, treats empty fields as NULL. Default is True.
            null_if (List[str], optional): List of strings to be treated as NULL values. Default is an empty list.

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.copy_from_s3(
                s3_prefix="prefix",
                s3_file="example_file",
                schema="example_schema",
                table="example_table",
                quotes=True,
                sep=",",
                empty_field_as_null=True,
                null_if=["NULL", "NA"]
            )
        """
        # Determine the appropriate formatting for the table name based on the 'quotes' parameter
        table_name = f'"{table.lower()}"' if quotes else table.upper()

        # Join null_if list elements into a comma-separated string
        list_null_if = ", ".join(f"'{case}'" for case in null_if)

        # Execute the Snowflake COPY INTO command from S3
        self.conn.cursor().execute(
            f"""
            COPY INTO {self.snowflake_database}.{schema.upper()}.{table_name}
            FROM s3://{os.environ.get("S3_BUCKET_DATAMART")}/{s3_prefix.lower()}/{s3_file.lower()}
            CREDENTIALS = (
            aws_key_id='{os.environ.get("AWS_ACCESS_KEY_ID")}',
            aws_secret_key='{os.environ.get("AWS_SECRET_ACCESS_KEY")}'
            )
            FILE_FORMAT=(field_delimiter='{sep}', SKIP_HEADER=1, FIELD_OPTIONALLY_ENCLOSED_BY='"', 
            NULL_IF=({list_null_if}), EMPTY_FIELD_AS_NULL = {str(empty_field_as_null).upper()}) 
            FORCE = TRUE;
            """
        )

    def create_table_from_template(
            self,
            table: str,
            staging_name: str,
            file_format_name: str,
            quotes: bool = False,
            ignore_identifiers_case: bool = True
    ) -> None:
        """
        Creates or replaces a Snowflake table using a template from Parquet files.

        Args:
            table (str): The name of the Snowflake table to create or replace.
            staging_name (str): The name of the Snowflake stage containing Parquet files.
            file_format_name (str): The name of the file format for Parquet files.
            quotes (bool, optional): If True, adds double quotes around the table name. Default is False.
            ignore_identifiers_case (bool, optional): If True, ignores case sensitivity in schema inference. Default is True.

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.create_table_from_template(
                table="example_table",
                staging_name="example_stage",
                file_format_name="parquet_format",
                quotes=True,
                ignore_identifiers_case=False
            )
        """
        # Determine the appropriate formatting for the table name based on the 'quotes' parameter
        table_name = f'"{table.lower()}"' if quotes else table.upper()

        # Execute the Snowflake CREATE OR REPLACE TABLE command using a template
        self.conn.cursor().execute(
            f"""
            CREATE OR REPLACE TABLE {self.snowflake_database}.{self.schema.upper()}.{table_name.upper()}
                USING TEMPLATE (
                    SELECT array_agg(object_construct(*))
                      FROM TABLE(
                        INFER_SCHEMA(
                          LOCATION=>'@{staging_name}',
                          FILE_FORMAT=>'{file_format_name}',
                          IGNORE_CASE=>{ignore_identifiers_case}
                        )
                      )
                );
            """
        )

    def create_parquet_file_format(
            self,
            file_format_name: str = "parquet_format"
    ) -> None:
        """
        Creates or replaces a Snowflake file format for Parquet files.

        Args:
            file_format_name (str, optional): The name of the file format. Default is "parquet_format".

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.create_parquet_file_format(file_format_name="custom_format")
        """
        # Execute the Snowflake CREATE OR REPLACE FILE FORMAT command
        self.conn.cursor().execute(
            f"""
            CREATE OR REPLACE FILE FORMAT {file_format_name} 
            type = PARQUET;
            """
        )

    def create_parquet_stage(
            self,
            table: str,
            staging_name: str,
            prefix: str = "migrate_parquet_to_snowflake_temp"
    ) -> None:
        """
        Creates or replaces a Snowflake stage for Parquet files.

        Args:
            table (str): The name of the Snowflake table associated with the Parquet files.
            staging_name (str): The name of the Snowflake stage.
            prefix (str, optional): Prefix for the S3 URL. Default is "migrate_parquet_to_snowflake_temp".

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.create_parquet_stage(
                table="example_table",
                staging_name="example_stage",
                prefix="custom_prefix"
            )
        """
        # Execute the Snowflake CREATE OR REPLACE STAGE command
        self.conn.cursor().execute(
            f"""
            CREATE OR REPLACE STAGE {staging_name}
            url='s3://{os.environ.get("S3_BUCKET_DATAMART")}/{prefix}/{self.schema.lower()}/{table.lower()}/'
            CREDENTIALS = (
            aws_key_id='{os.environ.get("AWS_ACCESS_KEY_ID")}',
            aws_secret_key='{os.environ.get("AWS_SECRET_ACCESS_KEY")}'
            )
            FILE_FORMAT = (TYPE = 'PARQUET');
            """
        )

    def order_table_columns(self, table, col_names_in_order, quotes: bool = False):
        """
        Creates or replaces a table with columns in the specified order.

        Args:
            table (str): The name of the Snowflake table to reorder columns.
            col_names_in_order (List[str]): List of column names in the desired order.
            quotes (bool, optional): If True, adds double quotes around the table name. Default is False.

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.order_table_columns(
                table="example_table",
                col_names_in_order=["column1", "column2", "column3"],
                quotes=True
            )
        """
        # Determine the appropriate formatting for the table name based on the 'quotes' parameter
        table_name = f'"{table.lower()}"' if quotes else table.upper()

        # Execute the Snowflake CREATE OR REPLACE TABLE command
        self.conn.cursor().execute(
            f"""
            CREATE OR REPLACE TABLE {self.snowflake_database}.{self.schema.upper()}.{table_name} AS
            SELECT {','.join(col_names_in_order)}
            FROM {self.snowflake_database}.{self.schema.upper()}.{table_name};
            """
        )

    def copy_into(
            self,
            table,
            col_names: List,
            staging_name: str,
            pattern: str = ".*.parquet",
            quotes: bool = False
    ):
        """
        Copies data from a staging area into a Snowflake table.

        Args:
            table (str): The name of the Snowflake table to copy data into.
            col_names (List[str]): List of column names in the specified order.
            staging_name (str): The name of the staging area from which to copy data.
            pattern (str, optional): Regular expression pattern for matching files in the staging area. Default is ".*.parquet".
            quotes (bool, optional): If True, adds double quotes around the table name. Default is False.

        Returns:
            None

        Raises:
            Any specific exceptions raised during Snowflake operations.

        Example:
            instance.copy_into(
                table="example_table",
                col_names=["column1", "column2", "column3"],
                staging_name="staging_area",
                pattern=".*.parquet",
                quotes=True
            )
        """
        # Determine the appropriate formatting for the table name based on the 'quotes' parameter
        table_name = f'"{table.lower()}"' if quotes else table.upper()

        # Ensure columns are in the specified order
        self.order_table_columns(table=table_name, col_names_in_order=col_names, quotes=False)

        # Execute the Snowflake COPY INTO command
        self.conn.cursor().execute(
            f"""
            COPY INTO {self.snowflake_database}.{self.schema.upper()}.{table_name}
            FROM (
                SELECT {'$1:' + ', $1:'.join(col_names)}
                FROM @{staging_name}
            )
            PATTERN = '{pattern}'
            FILE_FORMAT = (
                TYPE = 'parquet'
            );
            """
        )

    def correct_syntax(self, query: str, no_comments: bool = False) -> str:
        """
        Snowflake has a specific SQL syntax. If we get a SQL from another SGBD, we must firstly
        correct the syntax into the snowflake constraints.

        Args:
            query: String containing the SQL script.
            no_comments: If we want to keep the SQL comments as well or not. Recommended keeping as false.

        Returns: The same query but snowflake-compatible.
        """
        return convert_to_snowflake_syntax(query, no_comments)

    def execute_metadata_query(self, query: List[str], logging: bool = False, correct_syntax=False):
        """
        Execute SQL queries applying or not some syntax corrections.

        :param query:
        :param logging:
        :param correct_syntax:

        :return:
        """
        # The snowflake python API allows only one command per request. That's why we must split the input query into
        # a list of commands.
        # Also, snowflake has a specific SQL syntax. If we get a SQL from another database manager, we must firstly
        # correct the syntax into the snowflake constraints.
        if correct_syntax:
            queries_list = "".join(self.correct_syntax(command) for command in query if not re.match(r"^\s*$", command))
        else:
            queries_list = "".join(command for command in query if not re.match(r"^\s*$", command))
        queries_list = sqlparse.split(queries_list)

        for command in queries_list:
            try:
                self.conn.cursor().execute(f"{command.strip()};")
            except snowflake.connector.errors.ProgrammingError as e:
                if ("does not exist or not authorized" not in str(e)) or ("Empty SQL statement" not in str(e)):
                    if logging:
                        print(f"Problem found. Skipping command. Check the query_log_errors.txt for more details.")
                        log_file = open("query_log_errors.txt", "a+")
                        log_file.write(f"{command}\n")
                        print(e)
                        log_file.close()
                    else:
                        print(f"Problem found. Skipping command...")

    def execute_key_query(
            self,
            df: pd.DataFrame,
            key: str = "primary",
            logging: bool = False
    ) -> None:
        """
        Executes key-related SQL queries based on a DataFrame containing key information.

        Args:
            df (pd.DataFrame): DataFrame containing key information.
            key (str, optional): The type of key to handle ("primary" or "unique"). Default is "primary".
            logging (bool, optional): If True, logs errors to a file. Default is False.

        Returns:
            None
        """
        for row in range(df.__len__()):
            if key == "primary":
                if df.iloc[row, 2] != "":
                    drop_key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} DROP PRIMARY KEY;"
                    key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} ADD PRIMARY KEY ({df.iloc[row, 2]});"
                    skip = False
                else:
                    skip = True

            elif key == "unique":
                if (df.iloc[row, 3] != "") and (df.iloc[row, 3] != df.iloc[row, 2]):
                    drop_key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} DROP UNIQUE ({df.iloc[row, 3]});"
                    key_query = f"ALTER TABLE {df.iloc[row, 0]}.{df.iloc[row, 1]} ADD UNIQUE ({df.iloc[row, 3]});"
                    skip = False
                else:
                    skip = True

            if not skip:
                try:
                    # Execute the key_query
                    self.conn.cursor().execute(key_query)
                except snowflake.connector.errors.ProgrammingError as e:
                    if "already exists" in str(e):
                        # If the key already exists, drop it and re-execute the key_query
                        self.conn.cursor().execute(drop_key_query)
                        self.conn.cursor().execute(key_query)
                    else:
                        if ("does not exist or not authorized" not in str(e)) or ("Empty SQL statement" not in str(e)):
                            if logging:
                                # Log errors to a file if logging is enabled
                                print(f"Problem found. Skipping command. Check the query_log_errors.txt for more details.")
                                log_file = open("query_log_errors.txt", "a+")
                                log_file.write(f"{key_query}\n")
                                print(e)
                                log_file.close()
                            else:
                                print(f"Problem found. Skipping command...")
