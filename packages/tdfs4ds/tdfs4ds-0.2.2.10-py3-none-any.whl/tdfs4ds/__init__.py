__version__ = '0.2.2.10'

DATA_DOMAIN             = None
SCHEMA                  = None
FEATURE_CATALOG_NAME    = 'FS_FEATURE_CATALOG'
PROCESS_CATALOG_NAME    = 'FS_PROCESS_CATALOG'
DATA_DISTRIBUTION_NAME  = 'FS_DATA_DISTRIBUTION'
FILTER_MANAGER_NAME     = 'FS_FILTER_MANAGER'

END_PERIOD              = 'UNTIL_CHANGED' #'9999-01-01 00:00:00'
FEATURE_STORE_TIME      = None #'9999-01-01 00:00:00'
FEATURE_VERSION_DEFAULT = 'dev.0.0'
DISPLAY_LOGS            = True
DEBUG_MODE              = False

USE_VOLATILE_TABLE      = True
STORE_FEATURE           = 'MERGE' #'UPDATE_INSERT'
REGISTER_FEATURE        = 'MERGE' #'UPDATE_INSERT'
import warnings
warnings.filterwarnings('ignore')

import teradataml as tdml
from tdfs4ds.utils.lineage import crystallize_view
from tdfs4ds.utils.filter_management import FilterManager
import tdfs4ds.feature_store
import tdfs4ds.process_store
import tdfs4ds.datasets

import inspect
import tqdm

try:
    SCHEMA = tdml.context.context._get_current_databasename()
    if SCHEMA is None:
        print('Please specify the database which is hosting the feature store.')
        print('tdfs4ds.feature_store.schema = "<feature store database>"')
    else:
        print('The default database is used for the feature store.')
        print(f"tdfs4ds.feature_store.schema = '{SCHEMA}'")
        if DATA_DOMAIN is None:
            DATA_DOMAIN = SCHEMA
            print(f"the data domain for the current work is :{DATA_DOMAIN}")
            print("Please update it as you wish with tdfs4ds.DATA_DOMAIN=<your data domain>")

except Exception as e:
    print('Please specify the database which is hosting the feature store.')
    print('tdfs4ds.feature_store.schema = "<feature store database>"')


def setup(database, if_exists='fail'):
    """
    Set up the database environment by configuring schema names and optionally dropping existing tables.

    This function sets the database schema for feature and process catalogs. If specified, it also handles
    the replacement of existing catalog tables. It reports the status of these operations, including any
    encountered exceptions.

    Parameters:
    database (str): The name of the database schema to be used.
    if_exists (str, optional): Determines the behavior if catalog tables already exist in the database.
                               'fail' (default) - Do nothing if the tables exist.
                               'replace' - Drop the tables if they exist before creating new ones.

    Steps performed:
    1. Sets the schema to the provided database name.
    2. If 'if_exists' is 'replace', attempts to drop 'FS_FEATURE_CATALOG' and 'FS_PROCESS_CATALOG' tables.
    3. Creates new feature and process catalog tables and sets their names in the tdfs4ds module.
    4. Prints the names of the newly created tables along with the database name.
    5. Captures and prints the first line of any exceptions that occur during these operations.

    Returns:
    None
    """

    from tdfs4ds.feature_store.feature_store_management import feature_store_catalog_creation
    from tdfs4ds.process_store.process_store_catalog_management import process_store_catalog_creation

    tdfs4ds.SCHEMA = database
    if if_exists == 'replace':
        try:
            tdml.db_drop_table(table_name = tdfs4ds.FEATURE_CATALOG_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
        try:
            tdml.db_drop_table(table_name = tdfs4ds.PROCESS_CATALOG_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
        try:
            tdml.db_drop_table(table_name = tdfs4ds.DATA_DISTRIBUTION_NAME, schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
    try:
        tdfs4ds.FEATURE_CATALOG_NAME = feature_store_catalog_creation()
        print('feature catalog table: ', tdfs4ds.FEATURE_CATALOG_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    try:
        tdfs4ds.PROCESS_CATALOG_NAME, tdfs4ds.DATA_DISTRIBUTION_NAME = process_store_catalog_creation()
        print('process catalog table: ', tdfs4ds.PROCESS_CATALOG_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    return

def connect(database = tdfs4ds.SCHEMA, feature_catalog_name=tdfs4ds.FEATURE_CATALOG_NAME, process_catalog_name=tdfs4ds.PROCESS_CATALOG_NAME, data_distribution_name = tdfs4ds.DATA_DISTRIBUTION_NAME):
    """
    Set up the database environment by configuring schema names and optionally checks for the existence of feature and process catalogs.

    This function sets the database schema for feature and process catalogs based on the provided names. It verifies the existence of these catalog tables in the database and raises an assertion error if either or both are missing. It also sets the names of these catalogs in the tdfs4ds module if they exist.

    Parameters:
    - database (str): The name of the database schema to be used.
    - feature_catalog_name (str, optional): The name of the feature catalog. Defaults to tdfs4ds.FEATURE_CATALOG_NAME.
    - process_catalog_name (str, optional): The name of the process catalog. Defaults to tdfs4ds.PROCESS_CATALOG_NAME.

    Steps performed:
    1. Sets the schema to the provided database name.
    2. Checks if the specified feature and process catalog tables exist in the database.
    3. Sets the names of the existing feature and process catalog tables in the tdfs4ds module.
    4. Raises an assertion error if either or both catalog tables do not exist, with a specific message for each case.

    Returns:
    None

    Raises:
    AssertionError: If the feature catalog, the process catalog, or both do not exist in the database.
    """

    if database is not None:
        tdfs4ds.SCHEMA = database
    else:
        assert False, "database is None."
        return

    tables = [x.lower() for x in list(tdml.db_list_tables(schema_name=tdfs4ds.SCHEMA, object_type='table').TableName.values)]
    feature_exists = feature_catalog_name.lower() in tables
    process_exists = process_catalog_name.lower() in tables
    distrib_exists = data_distribution_name.lower() in tables

    if feature_exists and process_exists:
        tdfs4ds.FEATURE_CATALOG_NAME = feature_catalog_name
        tdfs4ds.PROCESS_CATALOG_NAME = process_catalog_name
    else:
        if not feature_exists and not process_exists and not distrib_exists:
            assert False, "feature catalog, process catalog and data distribution table do not exist."
        elif not feature_exists and not process_exists:
            assert False, "both feature catalog and process catalog do not exist."
        elif not feature_exists and not distrib_exists:
            assert False, "both feature catalog and data distribution table do not exist."
        elif not process_exists and not distrib_exists:
            assert False, "both process catalog and data distribution table do not exist."
        elif not feature_exists:
            assert False, "Feature catalog does not exist."
        elif not process_exists:
            assert False, "Process catalog does not exist."
        elif not distrib_exists:
            assert False, "Data distribution table does not exist."

    return

def feature_catalog():
    """
    Retrieve a list of all features available in the feature store.

    This function queries the feature store to obtain a comprehensive list of features
    that have been defined and stored. It leverages the feature store's query retrieval
    functionality to compile and return this list. This can be useful for understanding
    what features are available for analysis, machine learning models, or other purposes
    within the data ecosystem.

    Returns:
    - list: A list of features available in the feature store as a teradata dataframe at
            the tdfs4ds.FEATURE_STORE_TIME valid time.
    """
    return tdfs4ds.feature_store.feature_query_retrieval.list_features()


def process_catalog():
    """
    Retrieve a list of all processes registered in the process store.

    This function performs a query against the process store to gather a list of all
    processes that have been registered and are administrable. It utilizes the process
    store's process query administration capabilities to fetch and return this list.
    This is useful for users looking to get an overview of the data processing workflows,
    transformations, and other processes that have been established within the data
    infrastructure.

    Returns:
    - list: A list of processes registered in the process store as a teradata dataframe at
            the tdfs4ds.FEATURE_STORE_TIME valid time.
    """
    return tdfs4ds.process_store.process_query_administration.list_processes()



def run(process_id, return_dataset = False):
    """
    Executes a specific process from the feature store identified by the process ID.
    The function handles different process types and performs appropriate actions.

    Args:
    process_id (str): The unique identifier of the process to run.
    as_date_of (str, optional): Date parameter for the process execution. Defaults to None.

    Returns:
    None: The function returns None, but performs operations based on process type.
    """

    if tdfs4ds.DEBUG_MODE:
        print('def run','tdfs4ds.FEATURE_STORE_TIME', tdfs4ds.FEATURE_STORE_TIME)

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Construct SQL query to retrieve process details by process ID
    query = f"""
    {validtime_statement}
    SEL 
        A.*,
        B.FOR_PRIMARY_INDEX,
        CASE WHEN B.FOR_DATA_PARTITIONING IS NULL THEN '' ELSE B.FOR_DATA_PARTITIONING END AS FOR_DATA_PARTITIONING,
        D.DATABASE_NAME AS FILTER_DATABASE_NAME,
        D.VIEW_NAME AS FILTER_VIEW_NAME,
        D.TABLE_NAME AS FILTER_TABLE_NAME
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} A
    LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.DATA_DISTRIBUTION_NAME} B
    ON A.PROCESS_ID = B.PROCESS_ID
    LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FILTER_MANAGER_NAME} D
    ON A.PROCESS_ID = D.PROCESS_ID
    WHERE A.PROCESS_ID = '{process_id}' 
    """

    # Executing the query and converting the result to Pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Check if exactly one record is returned, else print an error
    if df.shape[0] != 1:
        print('error - there is ', df.shape[0], f' records. Check table {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}')
        print('check ou this query:')
        print(query)
        return


    # Fetching the filter manager
    filter_schema_name = df['FILTER_DATABASE_NAME'].values[0]
    if filter_schema_name is None:
        filtermanager = None
    else:
        filter_view_name = df['FILTER_VIEW_NAME'].values[0]
        filter_table_name = df['FILTER_TABLE_NAME'].values[0]
        filtermanager = FilterManager(table_name=filter_view_name, schema_name=filter_schema_name)

    # Fetching the process type from the query result
    process_type = df['PROCESS_TYPE'].values[0]

    # Fetching the primary index from the query result
    primary_index = df['FOR_PRIMARY_INDEX'].values[0]
    if primary_index is not None:
        primary_index = primary_index.split(',')

    # Fetching the primary index from the query result
    partitioning = df['FOR_DATA_PARTITIONING'].values[0]

    # Fetching the data domain from the query result
    DATA_DOMAIN = df['DATA_DOMAIN'].values[0]

    # Handling 'denormalized view' process type
    if process_type == 'denormalized view':
        # Extracting necessary details for this process type
        view_name = df['VIEW_NAME'].values[0]
        entity_id = eval(df['ENTITY_ID'].values[0])
        feature_names = df['FEATURE_NAMES'].values[0].split(',')

        # Fetching data and uploading features to the feature store
        df_data = tdml.DataFrame(tdml.in_schema(view_name.split('.')[0], view_name.split('.')[1]))

        if tdfs4ds.DEBUG_MODE:
            print('run','entity_id',entity_id)
            print('run','feature_names',feature_names)
            print('run','process_id',process_id)
            print('run','primary_index',primary_index)
            print('run','partitioning',partitioning)
        dataset = _upload_features(
            df_data,
            entity_id,
            feature_names,
            feature_versions = process_id,
            primary_index = primary_index,
            partitioning = partitioning,
            filtermanager = filtermanager
        )

    # Handling 'tdstone2 view' process type
    elif process_type == 'tdstone2 view':
        print('not implemented yet')

    if return_dataset:
        return dataset
    else:
        return

def upload_features(df, entity_id, feature_names, metadata={}, primary_index = None, partitioning = '', filtermanager = None):
    """
    Uploads feature data from a DataFrame to the feature store for a specified entity. This involves registering the
    process in the feature store, executing the necessary SQL to insert the data, and returning the resulting dataset
    for further use or inspection.

    The function supports dynamic entity ID interpretation and flexible feature name handling, ensuring compatibility
    with various data schemas. It automatically registers the data upload process and applies additional metadata,
    if provided.

    Parameters:
    - df (DataFrame): The DataFrame containing the feature data to be uploaded.
    - entity_id (dict, list, or str): The identifier of the entity to which the features belong. This can be:
        - a dictionary mapping column names to their data types,
        - a list of column names, which will be automatically converted to a dictionary with types inferred from `df`,
        - a string representing a single column name, which will be converted into a list and then to a dictionary as above.
    - feature_names (list or str): The names of the features to be uploaded. If a string is provided, it will be
      split into a list based on commas or treated as a single feature name.
    - metadata (dict, optional): Additional metadata to associate with the upload process. Defaults to an empty dictionary.
    - primary_index (list, optional): Specifies the primary index columns for optimizing data storage and retrieval.
    - partitioning (str, optional): Defines how the data should be partitioned in the store for performance optimization.

    Returns:
    DataFrame: A DataFrame representing the dataset resulting from the upload process, typically used for validation
               or further processing.

    The process involves several steps, including entity ID type conversion if necessary, feature name normalization,
    process registration in the feature store, and the execution of SQL queries to insert the data. The function concludes
    by returning a dataset derived from the uploaded data, offering immediate access to the newly stored information.

    Example:
    >>> df = tdml.DataFrame(...)
    >>> entity_id = ['customer_id']
    >>> feature_names = ['age', 'income']
    >>> dataset = upload_features(df, entity_id, feature_names)
    >>> # Another example with list-based entity_id, custom primary_index, and partitioning
    >>> tddf = tdml.DataFrame(...)  # Assuming tddf is predefined with appropriate columns
    >>> entity_id = ['tx_type', 'txn_id']
    >>> primary_index = ['txn_id']
    >>> partitioning = '''
    ... PARTITION BY CASE_N (
    ...     tx_type LIKE 'DEBIT',
    ...     tx_type LIKE 'PAYMENT',
    ...     tx_type LIKE 'CASH_OUT',
    ...     tx_type LIKE 'CASH_IN',
    ...     tx_type LIKE 'TRANSFER',
    ...     NO CASE,
    ...     UNKNOWN)'''
    >>> features = [x for x in tddf.columns if x not in entity_id]
    >>> dataset = upload_features(
    ...     df = tddf,
    ...     entity_id = entity_id,
    ...     feature_names = features,
    ...     metadata = {'project': 'test'},
    ...     primary_index = primary_index,
    ...     partitioning = partitioning
    ... )
    """

    from tdfs4ds.utils.info import get_column_types
    from tdfs4ds.utils.query_management import execute_query
    from tdfs4ds.process_store.process_registration_management import register_process_view

    # Convert entity_id to a dictionary if it's not already one
    if type(entity_id) == list:
        entity_id.sort()
        entity_id = get_column_types(df, entity_id)
        print('entity_id has been converted to a proper dictionary : ', entity_id)
    elif type(entity_id) == str:
        entity_id = [entity_id]
        entity_id = get_column_types(df, entity_id)
        print('entity_id has been converted to a proper dictionary : ', entity_id)

    if type(feature_names) != list:
        if tdfs4ds.DISPLAY_LOGS:
            print('feature_names is not a list:', feature_names)
        if ',' in feature_names:
            feature_names = feature_names.split(',')
        else:
            feature_names = [feature_names]
        if tdfs4ds.DISPLAY_LOGS:
            print('it has been converted to : ', feature_names)
            print('check it is a expected.')

    if tdfs4ds.DISPLAY_LOGS:
        print("filtermanager", filtermanager)

    # Register the process and retrieve the SQL query to insert the features, and the process ID
    query_insert, process_id, query_insert_dist, query_insert_filtermanager = register_process_view.__wrapped__(
        view_name       = df,
        entity_id       = entity_id,
        feature_names   = feature_names,
        metadata        = metadata,
        with_process_id = True,
        primary_index   = primary_index,
        partitioning    = partitioning,
        filtermanager   = filtermanager
    )

    # Execute the SQL query to insert the features into the database
    execute_query(query_insert)
    execute_query(query_insert_dist)
    print("query_insert_filtermanager",query_insert_filtermanager)
    if query_insert_filtermanager is not None:
        execute_query(query_insert_filtermanager)

    # Run the registered process and return the resulting dataset
    dataset = run(process_id=process_id, return_dataset=True)

    return dataset

def _upload_features(df, entity_id, feature_names,
                   feature_versions=FEATURE_VERSION_DEFAULT, primary_index = None, partitioning = '', filtermanager=None):
    """
    Uploads features from a DataFrame to the feature store, handling entity registration, feature type determination,
    feature registration, preparation for ingestion, and storage in the designated feature tables.

    Parameters:
    - df (DataFrame): The input DataFrame containing the feature data.
    - entity_id (str or dict): The identifier for the entity to which these features belong. This can be a single ID
                               (str) or a dictionary of attribute names and values uniquely identifying the entity.
    - feature_names (list): A list of strings specifying the names of the features to be uploaded.
    - feature_versions (str or list, optional): Specifies the versions of the features to be uploaded. Can be a single
                                                string applied to all features or a list of strings specifying the version
                                                for each feature respectively. Default is 'dev.0.0'.
    - primary_index (list, optional): Specifies the columns to be used as the primary index in the feature store tables.
                                      This can significantly impact the performance of data retrieval operations.
    - partitioning (str, optional): A string indicating the partitioning strategy for the feature store tables, which can
                                    enhance query performance based on the access patterns.

    Returns:
    DataFrame: A DataFrame representing the dataset view created in the feature store, detailing the features and their
               metadata, including versions and storage locations.

    This function orchestrates several steps involved in feature storage:
    1. Registers the entity in the feature store if not already present.
    2. Determines the data types of the features based on the input DataFrame.
    3. Registers the features, including their names, types, and versions, in the feature catalog.
    4. Prepares the feature data for ingestion, including any necessary transformations.
    5. Stores the prepared feature data in the feature store.
    6. Optionally, cleans up temporary resources used during the process.
    7. Builds and returns a view of the dataset representing the uploaded features for easy access.

    Note:
    - The function relies on various sub-modules within the `tdfs4ds` library for different steps of the process, from
      entity and feature registration to data preparation and storage.
    - It is intended to be used internally within a system that manages a Teradata feature store, assuming access to
      a Teradata database and the appropriate schema for feature storage.
    - The function assumes that the feature_versions, if provided as a list, matches the length of feature_names.
    """
    from tdfs4ds.feature_store.entity_management import register_entity
    from tdfs4ds.feature_store.feature_store_management import Gettdtypes
    from tdfs4ds.feature_store.feature_store_management import register_features
    from tdfs4ds.feature_store.feature_data_processing import prepare_feature_ingestion
    from tdfs4ds.feature_store.feature_data_processing import store_feature

    register_entity(entity_id, primary_index=primary_index, partitioning=partitioning)

    # If feature_versions is a list, create a dictionary mapping each feature name to its corresponding version.
    # If feature_versions is a string, create a dictionary mapping each feature name to this string.
    if type(feature_versions) == list:
        selected_features = {k: v for k, v in zip(feature_names, feature_versions)}
    else:
        selected_features = {k: feature_versions for k in feature_names}

    # Get the Teradata types of the features in df.
    feature_names_types = Gettdtypes(
        df,
        features_columns=feature_names,
        entity_id=entity_id
    )

    if tdfs4ds.DEBUG_MODE:
        print('_upload_features', 'entity_id', entity_id)
        print('_upload_features', 'feature_names', feature_names)
        print('_upload_features', 'primary_index', primary_index)
        print('_upload_features', 'partitioning', partitioning)

    # Register the features in the feature catalog.
    register_features(
        entity_id,
        feature_names_types,
        primary_index,
        partitioning
    )
    if tdfs4ds.DISPLAY_LOGS:
        print("filtermanager",filtermanager)
    if filtermanager is None:
        # Prepare the features for ingestion.
        prepared_features, volatile_table_name = prepare_feature_ingestion(
            df,
            entity_id,
            feature_names,
            feature_versions=selected_features
        )

        # Store the prepared features in the feature store.
        store_feature(
            entity_id,
            prepared_features
        )
    else:
        nb_filters = filtermanager.nb_filters
        for i in range(nb_filters):
            filtermanager.update(i+1)
            if tdfs4ds.DISPLAY_LOGS:
                print(filtermanager.display())
            # Prepare the features for ingestion.
            prepared_features, volatile_table_name = prepare_feature_ingestion(
                df,
                entity_id,
                feature_names,
                feature_versions=selected_features
            )

            # Store the prepared features in the feature store.
            store_feature(
                entity_id,
                prepared_features
            )

            # Clean up by dropping the temporary volatile table.
            tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Build a dataset view in the feature store.
    dataset = build_dataset(
        entity_id,
        selected_features,
        view_name=None
    )

    # Return the dataset view.
    return dataset

def build_dataset(entity_id, selected_features, view_name,
                  comment='dataset', no_temporal=False, time_manager=None, query_only=False):
    """
    This function builds a dataset view in a Teradata database. It is designed to pivot and format data from the feature catalog and feature tables based on the specified parameters.

    Parameters:
    - entity_id (dict or list or other): A dictionary, list, or other format representing the entity ID. The keys of the dictionary are used to identify the entity. Lists and other formats are converted to a list of keys.
    - selected_features (dict): A dictionary specifying the selected features and their corresponding feature versions.
    - view_name (str): The name of the dataset view to be created.
    - comment (str, optional): A comment to associate with the dataset view. Defaults to 'dataset'.
    - no_temporal (bool, optional): Flag to determine if temporal aspects should be ignored. Defaults to False.
    - time_manager (object, optional): An object to manage time aspects. Defaults to None.
    - query_only (bool, optional): Flag to determine if we want only the generated query without the execution

    Returns:
    tdml.DataFrame: A DataFrame representing the dataset view.
    """

    from tdfs4ds.utils.query_management import execute_query

    # Retrieve feature data from the feature catalog table
    feature_catalog = tdml.DataFrame.from_query(f'CURRENT VALIDTIME SELECT * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}')

    # Determine the valid time statement based on the presence of a specific date in the past
    if tdfs4ds.FEATURE_STORE_TIME is None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Adjust valid time statement based on the presence of time_manager and no_temporal flag
    if no_temporal:
        validtime_statement = ''

    # Convert entity_id to a list format for processing
    if isinstance(entity_id, list):
        list_entity_id = entity_id
    elif isinstance(entity_id, dict):
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Compose the entity names and retrieve the corresponding feature locations
    ENTITY_NAMES = ','.join([k for k in list_entity_id])
    ENTITY_ID = ', \n'.join([k for k in list_entity_id])
    if len(selected_features) > 1:
        ENTITY_ID_ = ','.join([','.join(['COALESCE('+','.join(['AA'+str(i+1)+'.'+k for i,c in enumerate(selected_features)])+') as '+k]) for k in list_entity_id])
    else:
        ENTITY_ID_ = ','.join([','.join(['' + ','.join(['AA' + str(i + 1) + '.' + k for i, c in enumerate(selected_features)]) + ' as ' + k]) for k in list_entity_id])


    feature_location = feature_catalog[(feature_catalog.FEATURE_NAME.isin(list(selected_features.keys()))) & \
                                        (feature_catalog.ENTITY_NAME == ENTITY_NAMES) & \
                                        (feature_catalog.DATA_DOMAIN == DATA_DOMAIN) \
                                       ].to_pandas()

    # manage the case sensitivity
    feature_location['FEATURE_NAME_UPPER'] = [x.upper() for x in feature_location['FEATURE_NAME']]
    feature_location['FEATURE_VERSION'] = feature_location['FEATURE_NAME_UPPER'].map({k.upper():v for k,v in selected_features.items()})


    # Build the query to retrieve the selected features from the feature tables
    query = []
    counter = 1
    feature_names = []
    for g,df in feature_location.groupby(['FEATURE_DATABASE','FEATURE_TABLE']):
        for i,row in df.iterrows():
            condition = ' \n '+f"(FEATURE_ID = {row['FEATURE_ID']} AND FEATURE_VERSION = '{row['FEATURE_VERSION']}')"
            if time_manager is not None:
                if 'date' in time_manager.data_type.lower():
                    if DISPLAY_LOGS:
                        print(f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
                    query_ = f"""
                    SELECT  A{counter}.* FROM (
                    SELECT * FROM {g[0]}.{g[1]}
                    WHERE  {condition} AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})
                    ) A{counter}
                    """
                else:
                    if DISPLAY_LOGS:
                        print(
                        f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
                    query_ = f"""
                    SELECT  A{counter}.* FROM (
                    SELECT * FROM {g[0]}.{g[1]}
                    WHERE  {condition} AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})
                    ) A{counter}
                    """
            else:
                if DISPLAY_LOGS:
                    print(f'no time manager used.')
                query_ = f"""
                SELECT  A{counter}.* FROM (
                {validtime_statement} SELECT * FROM {g[0]}.{g[1]}
                WHERE  {condition}
                ) A{counter}
                """
            query.append(query_)
            feature_names.append(row['FEATURE_NAME'])
            counter+=1



    query_select  = [f"SELECT {ENTITY_ID_}"]
    query_select  = query_select + ['AA'+str(i+1)+'.FEATURE_VALUE AS '+c for i,c in enumerate(feature_names)]
    if no_temporal:
        query_select = query_select + ['AA'+str(i+1)+'.ValidStart AS ValidStart_'+ c + ',AA'+str(i+1)+'.ValidEnd AS ValidEnd_'+ c for i,c in enumerate(feature_names)]
    query_select  = ', \n'.join(query_select)

    query_from    = [' FROM ('+query[0]+') AA1 ']
    query_from    = query_from + [' FULL OUTER JOIN ('+q+') AA'+str(i+1)+' \n ON '+' \n AND '.join([f'AA1.{c}=AA{i+1}.{c}' for c in list_entity_id]) for i,q in enumerate(query) if i>0]
    query_from    = '\n'.join(query_from)

    query_dataset = query_select + '\n' + query_from

    # Build the query to create the dataset view by pivoting the feature data
    query_create_view = f'REPLACE VIEW {SCHEMA}.{view_name} AS'
    query_pivot = f"""
    {query_dataset} 
    """

    if tdml.display.print_sqlmr_query:
        print(query_create_view+'\n'+query_pivot)
    if query_only:
        return query_pivot
    else:
        if view_name != None:
            execute_query(query_create_view+'\n'+query_pivot)
            execute_query(f"COMMENT ON VIEW {SCHEMA}.{view_name} IS '{comment}'")
            if DISPLAY_LOGS: print(f'the dataset view {SCHEMA}.{view_name} has been created')

            return tdml.DataFrame(tdml.in_schema(SCHEMA, view_name))
        else:
            return tdml.DataFrame.from_query(query_pivot)

def _build_time_series(entity_id, selected_feature, query_only=False):
    """
    Constructs a time series dataset for a given entity and feature.
    Optionally returns only the query used for dataset construction.

    This is a wrapper around the `build_dataset` function, tailored specifically for time series data by setting temporal parameters to null.

    Args:
        entity_id (dict): The identifier for the entity for which the dataset is being built.
        selected_feature (str or list): The feature(s) to be included in the dataset.
        query_only (bool, optional): If True, returns only the SQL query used for building the dataset, not the dataset itself. Defaults to False.

    Returns:
        DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
    """

    # Call the build_dataset function with specific parameters set for time series dataset construction
    return build_dataset(
        entity_id         = entity_id,  # The identifier for the entity
        selected_features = selected_feature,  # The feature(s) to be included in the dataset
        no_temporal       = True,  # Indicates that the dataset should not have a temporal component
        query_only        = query_only,  # Determines whether to return just the query or the constructed dataset
        time_manager      = None,  # No time management for the dataset construction
        view_name         = None  # No specific view name provided
    )


def build_dataset_time_series(df, time_column, entity_id, selected_features, query_only=False, time_manager=None):
    """
    Constructs a time series dataset based on the specified features and entity_id from the provided dataframe.

    Args:
        df (DataFrame): The source dataframe.
        time_column (str): The name of the column in df that represents time.
        entity_id (dict): A dictionary representing the entity identifier.
        selected_features (dict): A dictionary with keys as feature names and values as conditions or specifications for those features.
        query_only (bool, optional): If True, only the SQL query for the dataset is returned. Defaults to False.
        time_manager (TimeManager, optional): An instance of TimeManager to manage time-related operations. Defaults to None.

    Returns:
        DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
    """

    # Convert column names to lowercase for case-insensitive matching
    col = [c.lower() for c in df.columns]

    # Check if the entity_id keys are present in the dataframe columns
    for e in entity_id:
        if e.lower() not in col:
            print(f' {e} is not present in your dataframe')
            print('Here are the columns of your dataframe:')
            print(str(col))
            return  # Exit if any entity_id key is not found

    # Check if the time_column is present in the dataframe columns
    if time_column.lower() not in col:
        print(f' {time_column} is not present in your dataframe')
        print('Here are the columns of your dataframe:')
        print(str(col))
        return  # Exit if the time_column is not found

    # Extract and check the data type of the time_column
    d_ = {x[0]: x[1] for x in df._td_column_names_and_types}
    time_column_data_type = d_[time_column]
    print('time column data type :', time_column_data_type)
    if 'date' not in time_column_data_type.lower() and 'time' not in time_column_data_type.lower():
        print('the time column of your data frame is neither a date nor a timestamp')
        return  # Exit if the time_column data type is not date or timestamp

    # Initialize the select query
    select_query = 'SELECT \n' + ', \n'.join(['A.' + c for c in col]) + '\n'

    # If a time_manager is provided, extract its details
    if time_manager is not None:
        tm_datatype = time_manager.data_type.lower()
        tm_schema = time_manager.schema_name
        tm_table = time_manager.table_name

    sub_queries_list = []
    # For each selected feature, build its part of the query
    for i, (k, v) in enumerate(selected_features.items()):
        select_query += ', BB' + str(i + 1) + '.' + k + '\n'

        nested_query = _build_time_series(entity_id, {k: v}, query_only=True)

        sub_queries = 'SELECT \n' + '\n ,'.join(entity_id) + '\n ,' + k + '\n'

        # Build the sub_queries based on the presence of a time_manager and the data types of time_column and time_manager
        if time_manager is None:
            # there is a time manager
            if 'date' in tm_datatype:
                # the data type of the time column is DATE
                sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart \n'
                sub_queries += f',	CAST(ValidEnd_{k} AS DATE) AS ValidEnd \n'
            else:
                # the data type of the time column is timestamp
                sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart \n'
                sub_queries += f',	CAST(ValidEnd_{k} AS TIMESTAMP(0)) AS ValidEnd \n'
        else:
            # there is a time manager

            if 'date' in time_column_data_type.lower():
                # the data type of the time column is DATE
                if 'date' in tm_datatype:
                    time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' DAY)"
                    # the data type of the time manager is DATE
                    sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart_ \n'
                    sub_queries += f",	CASE WHEN CAST(ValidEnd_{k} AS DATE) > {time_cursor} AND CAST(ValidStart_{k} AS DATE) < {time_cursor} THEN {time_cursor} ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd_ \n"
                else:
                    time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' SECOND)"
                    # the data type of the time manager is timestamp
                    sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart_ \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS DATE) > {time_cursor} AND CAST(ValidStart_{k} AS DATE) < {time_cursor} THEN {time_cursor} ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd_ \n'
            else:
                # the data type of the time column is TIMESTAMP
                if 'date' in tm_datatype:
                    time_cursor = "(BUS_DATE.BUSINESS_DATE + INTERVAL '1' DAY)"
                    sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart_ \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST({time_cursor} AS TIMESTAMP(0)) AND CAST(ValidStart_{k} AS TIMESTAMP(0)) < CAST({time_cursor} AS TIMESTAMP(0)) THEN CAST({time_cursor} AS TIMESTAMP(0)) ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd_ \n'
                else:
                    sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart_ \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST({time_cursor} AS TIMESTAMP(0)) AND CAST(ValidStart_{k} AS TIMESTAMP(0)) < CAST({time_cursor} AS TIMESTAMP(0)) THEN CAST({time_cursor} AS TIMESTAMP(0)) ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd_ \n'
        sub_queries += ',   PERIOD(ValidStart_, ValidEnd_) as PERIOD_ \n'
        sub_queries += f'FROM ({nested_query}) tmp{i + 1} \n'
        if time_manager is not None:
            sub_queries += f',{tm_schema}.{tm_table} BUS_DATE \n'

        sub_queries += 'WHERE ValidStart_ < ValidEnd_ \n'

        sub_queries = 'LEFT JOIN ( \n' + sub_queries + ') BB' + str(i + 1) + '\n ON '

        sub_queries += '\n  AND '.join(['A.' + c + '=BB' + str(i + 1) + '.' + c for c in entity_id])


        #sub_queries += f'\n AND PERIOD(BB{i + 1}.ValidStart_, BB{i + 1}.ValidEnd_) CONTAINS A.{time_column} \n'
        sub_queries += f'\n AND BB{i + 1}.PERIOD_ CONTAINS A.{time_column} \n'

        sub_queries_list.append(sub_queries)

    # Combine all parts of the query
    query = select_query + f'FROM ({df.show_query()}) A \n' + '\n --------------- \n'.join(sub_queries_list)

    if tdfs4ds.DEBUG_MODE:
        print('------------- BUILD DATASET TIMESERIES ---------------')
        print(query)
    # If only the query is requested, return it; otherwise, execute the query and return the resulting DataFrame
    if query_only:
        return query
    else:
        return tdml.DataFrame.from_query(query)

def upload_tdstone2_scores(model):
    """
    Uploads features from a model's predictions to the Teradata feature store. This function handles the entire
    workflow from extracting feature names and types, registering them in the feature catalog, preparing features for ingestion,
    storing them in the feature store, and finally creating a dataset view in the feature store.

    Parameters:
    - model: The model object whose predictions contain features to be uploaded. This model should have methods
      to extract predictions and feature information.

    Returns:
    - DataFrame: A DataFrame representing the dataset view created in the feature store, which includes
      features from the model's predictions.

    Note:
    - The function assumes that the model provides a method `get_model_predictions` which returns a Teradata DataFrame.
    - Entity ID for the model is extracted and registered in the data domain.
    - The function cleans up by dropping the volatile table created during the process.
    - The feature names and their types are extracted from the model's predictions and are registered in the feature catalog.
    """

    from tdfs4ds.feature_store.entity_management import register_entity
    from tdfs4ds.feature_store.entity_management import tdstone2_entity_id
    from tdfs4ds.feature_store.feature_store_management import tdstone2_Gettdtypes
    from tdfs4ds.feature_store.feature_store_management import register_features
    from tdfs4ds.feature_store.feature_data_processing import prepare_feature_ingestion_tdstone2
    from tdfs4ds.feature_store.feature_data_processing import store_feature

    # Extract the entity ID from the existing model.
    entity_id = tdstone2_entity_id(model)

    # Register the entity ID in the data domain.
    register_entity(entity_id)

    # Get the Teradata types of the features from the model's predictions.
    feature_names_types = tdstone2_Gettdtypes(model,entity_id)

    # Register these features in the feature catalog.
    register_features(entity_id, feature_names_types)

    # Prepare the features for ingestion into the feature store.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_model_predictions(),
            entity_id
        )
    else:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_computed_features(),
            entity_id
        )

    # Store the prepared features in the feature store.
    store_feature(entity_id, prepared_features)

    # Clean up by dropping the temporary volatile table.
    tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Get the list of selected features for building the dataset view.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        selected_features = model.get_model_predictions().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']
    else:
        selected_features = model.get_computed_features().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']

    # Build and return the dataset view in the feature store.
    dataset = build_dataset(entity_id, selected_features, view_name=None)
    return dataset


def roll_out(date_list, process_list, time_manager):
    """
    Executes a series of processes for each date in a given list, managing the time and logging settings.

    This function iterates over a list of dates, updating a TimeManager object with each date, and then
    executes a list of processes for that date. It also manages the synchronization of time for a feature store
    and disables display logs during its execution.

    Parameters:
    date_list (list): A list of dates for which the processes need to be executed.
    process_list (list): A list of process IDs that need to be executed for each date.
    time_manager (TimeManager object): An object that manages time-related operations, like updating or retrieving time.

    Side Effects:
    - Sets global variables DISPLAY_LOGS and FEATURE_STORE_TIME.
    - Catches and prints exceptions along with the date on which they occurred.
    """

    #global DISPLAY_LOGS
    #global FEATURE_STORE_TIME

    # Disable display logs
    temp_DISPLAY_LOGS = tdfs4ds.DISPLAY_LOGS
    tdfs4ds.DISPLAY_LOGS = False

    try:

        pbar = tqdm.tqdm(date_list, desc="Starting")
        # Iterate over each date in the provided list
        for date_ in pbar:
            pbar.set_description(f"Processing {date_}")
            # Update the time manager with the new date
            time_manager.update(new_time=date_)
            # Synchronize the time for the feature store with the current date
            tdfs4ds.FEATURE_STORE_TIME = time_manager.get_date_in_the_past()
            pbar.set_description(f"Processing {tdfs4ds.FEATURE_STORE_TIME}")
            if tdfs4ds.DEBUG_MODE:
                print('def roll_out','date_', date_)
                print('def roll_out','time_manager.get_date_in_the_past()', time_manager.get_date_in_the_past())
                print('def roll_out','tdfs4ds.FEATURE_STORE_TIME', tdfs4ds.FEATURE_STORE_TIME)
            # Execute each process in the process list for the current date
            for proc_id in process_list:
                pbar.set_description(f"Processing {date_} process {proc_id}")
                run(process_id=proc_id)
        tdfs4ds.DISPLAY_LOGS = temp_DISPLAY_LOGS
    except Exception as e:
        tdfs4ds.DISPLAY_LOGS = temp_DISPLAY_LOGS
        # If an exception occurs, print the date and the first line of the exception message
        print(date_)
        print(str(e).split('\n')[0])
