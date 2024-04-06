import teradataml as tdml
import tdfs4ds

def list_features():
    """
    Retrieves and returns a list of features from a feature store as a DataFrame.

    This function constructs a SQL query to select all features from a specific catalog within a schema, optionally
    using a specific valid time if set. It supports temporal querying by allowing the selection of features as of a
    certain timestamp, if `FEATURE_STORE_TIME` is specified in the `tdfs4ds` configuration. If `FEATURE_STORE_TIME` is
    not set, it defaults to querying the current valid time. The function then executes this query and returns the
    result as a DataFrame.

    Returns:
        tdml.DataFrame: A DataFrame containing the list of features from the feature store.

    Note:
        - This function requires the `tdfs4ds` and `tdml` libraries. `tdfs4ds` is assumed to be a configuration module
          or object that contains settings for connecting to a feature store, including `FEATURE_STORE_TIME`, `SCHEMA`,
          and `FEATURE_CATALOG_NAME`.
        - `FEATURE_STORE_TIME` is used to define a specific timestamp for querying the feature data, enabling temporal
          feature querying. If `FEATURE_STORE_TIME` is None, the query defaults to the current valid time.
        - The function constructs a SQL query using the specified `SCHEMA` and `FEATURE_CATALOG_NAME` from `tdfs4ds`,
          along with the determined valid time statement.
        - It is assumed that `tdml.DataFrame.from_query` method is capable of executing the SQL query and returning the
          result as a DataFrame.
    """
    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    query = f"{validtime_statement} SEL * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}"

    return tdml.DataFrame.from_query(query)


def get_feature_store_table_name(entity_id, feature_type, data_domain=None, primary_index=None, partitioning=''):
    """
    Constructs names for a database table and a corresponding view within a feature store, using the provided entity attributes, feature type, optional data domain, primary index, and partitioning information.

    This function generates names that are intended for organizing and accessing features in a structured manner within a feature store. The naming convention integrates various elements, including a prefix (indicating tables or views), the specified data domain (or a default one), and aspects of the entity ID, ensuring uniqueness and clarity in the schema.

    Parameters:
    - entity_id (dict, list, str, int): The identifier(s) for the entity. This can be:
        - a dictionary with keys representing entity attributes,
        - a list of attributes, or
        - a single attribute (string or integer).
      The function constructs the base part of the table and view names differently based on the type of `entity_id`.
    - feature_type (str): Specifies the type of feature, contributing to the naming to indicate the kind of data stored.
    - data_domain (str, optional): The categorization under which the table and view will be organized. If not provided, a default value from `tdfs4ds.DATA_DOMAIN` is used.
    - primary_index (list, optional): Specifies the primary index attributes. If not provided, it defaults to the attributes derived from `entity_id`. This influences the order and inclusion of entity attributes in the name.
    - partitioning (str, optional): A string containing attributes used for partitioning, separated by spaces or commas. This affects how the name indicates the data partitioning strategy.

    Returns:
    - tuple: Contains two strings; the first is the table name, and the second is the view name. These are constructed based on the input parameters to fit within a feature store's schema.

    Example:
    - For `entity_id={'customer_id': 123}`, `feature_type='purchase_history'`, `data_domain='retail'`, `primary_index=['customer_id']`, and `partitioning='year, month'`, this function would generate names like 'FS_T_retail_CUSTOMER_ID__YEAR_MONTH__PURCHASE_HISTORY' and 'FS_V_retail_CUSTOMER_ID__YEAR_MONTH__PURCHASE_HISTORY'.

    Note:
    - Assumes the presence of a `tdfs4ds` module with a `DATA_DOMAIN` constant for default data domain usage.
    - Designed for flexibility in entity ID specification, supporting simple IDs, attribute lists, or attribute key dictionaries.
    """
    import re

    # Set the data domain to the default if not specified
    if data_domain is None:
        data_domain = tdfs4ds.DATA_DOMAIN

    # Prepare entity ID list based on its type for further processing
    if isinstance(entity_id, list):
        list_entity_id = entity_id
    elif isinstance(entity_id, dict):
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Normalize entity ID attributes to uppercase for consistency
    entity_id_list = [x.upper() for x in list_entity_id]
    entity_id_list.sort()

    # Set primary index based on entity_id_list if not provided, then sort and normalize
    if primary_index is None:
        primary_index = entity_id_list
    elif type(primary_index) == str:
        primary_index = primary_index.split(',')
    primary_index = [x.upper() for x in primary_index]
    primary_index.sort()

    # Determine partitioning and other attributes for inclusion in the names
    partitioning_names = [k for k in entity_id_list if re.search(r'\b' + re.escape(k.upper()) + r'\b', partitioning.upper())]
    other_names = [k for k in entity_id_list if (k not in partitioning_names and k not in primary_index)]

    if tdfs4ds.DEBUG_MODE:
        print('get_feature_store_table_name','data_domain', data_domain)
        print('get_feature_store_table_name','primary_index', primary_index)
        print('get_feature_store_table_name','partitioning', partitioning)
        print('get_feature_store_table_name','partitioning_names',partitioning_names)
        print('get_feature_store_table_name','other_names',other_names)
    root_name = data_domain + '_' + '_'.join(primary_index)
    if partitioning != '':
        root_name += '__' + '_'.join(partitioning_names)
    if len(other_names)>0:
        root_name += '__' + '_'.join(other_names)
    root_name += '_' + feature_type

    table_name = 'FS_T_' + root_name
    view_name  = 'FS_V_' + root_name

    return table_name, view_name


def get_available_features(entity_id, display_details=False):
    """
    Retrieves the names of available features for a given entity ID from a feature store.

    This function constructs and executes a SQL query to select feature names from a specific catalog within a schema
    for a given entity ID, optionally using a specific valid time if set in `tdfs4ds.FEATURE_STORE_TIME`. The function
    supports querying features as of a certain timestamp or the current valid time if no timestamp is specified. It
    also provides an option to display detailed information about the features.

    Parameters:
        entity_id (str, list, or dict): The ID of the entity for which to retrieve available features. This can be a
                                        single ID (str), a list of IDs, or a dictionary of IDs where keys are entity
                                        names and values are their corresponding IDs.
        display_details (bool, optional): If True, prints detailed information about all features in the catalog.
                                          Defaults to False.

    Returns:
        list: A list of feature names available for the specified entity ID.

    Note:
        - `tdfs4ds` is assumed to be a configuration module or object containing settings for the feature store,
          including `FEATURE_STORE_TIME`, `SCHEMA`, `FEATURE_CATALOG_NAME`, `DATA_DOMAIN`, and `DEBUG_MODE`.
        - The entity ID(s) are used to filter the features specific to the entity. If `entity_id` is a dictionary,
          the keys are considered as entity names, and their values are IDs. If it's a list, it's assumed to be a list
          of entity names or IDs. For a single string, it is treated as a single entity name or ID.
        - `FEATURE_STORE_TIME` is used to determine the temporal context for querying the feature data. If it is None,
          the query defaults to the current valid time.
        - If `DEBUG_MODE` is enabled in `tdfs4ds`, the constructed query is printed to the console.
        - The function uses `tdml.DataFrame.from_query` to execute the SQL query and `to_pandas` to convert the result
          into a pandas DataFrame for further processing.
    """
    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    if type(entity_id) == dict:
        ENTITY_ID__ = ','.join([k.lower() for k, v in entity_id.items()])
    elif type(entity_id) == list:
        ENTITY_ID__ = ','.join([k.lower() for k in entity_id])
    else:
        ENTITY_ID__ = entity_id.lower()

    query = f"""
    {validtime_statement}
    SELECT 
          FEATURE_NAME
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
    WHERE LOWER(ENTITY_NAME) = '{ENTITY_ID__}'
    AND DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
    """

    if tdfs4ds.DEBUG_MODE:
        print(query)

    if display_details:
        print(tdml.DataFrame.from_query(f'{validtime_statement} SELECT * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}'))

    return list(tdml.DataFrame.from_query(query).to_pandas().FEATURE_NAME.values)

def get_list_entity(domain=None):
    """
    Retrieve a list of unique entity names from a specified data domain.

    This function executes a database query to extract distinct entity names from
    a feature catalog, filtered by the provided data domain. If no domain is
    specified, it defaults to a predefined data domain.

    Parameters:
    domain (str, optional): The data domain to filter the entity names.
                            Defaults to None, in which case a predefined domain is used.

    Returns:
    DataFrame: A pandas-like DataFrame containing the unique entity names.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Use the default data domain if none is specified
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Constructing the SQL query to fetch distinct entity names from the specified domain
    query = f"{validtime_statement} SEL DISTINCT ENTITY_NAME FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where DATA_DOMAIN = '{domain}'"

    # Executing the query and returning the result as a DataFrame
    return tdml.DataFrame.from_query(query)


def get_list_features(entity_name, domain=None):
    """
    Retrieve a list of feature names associated with a specific entity or entities
    from a given data domain.

    This function constructs and executes a database query to extract feature names
    for the specified entity or entities from a feature catalog, filtered by the
    provided data domain. If no domain is specified, it defaults to a predefined
    data domain.

    Parameters:
    entity_name (str or list): The name of the entity or a list of entity names
                               to fetch features for.
    domain (str, optional): The data domain to filter the feature names.
                            Defaults to None, where a predefined domain is used.

    Returns:
    DataFrame: A pandas-like DataFrame containing the feature names associated with the given entity or entities.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Default to a predefined data domain if none is provided
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Convert the entity_name to a string if it is a list
    if type(entity_name) == list:
        entity_name = ','.join(entity_name)

    # Constructing the SQL query to fetch feature names for the specified entity or entities
    query = f"{validtime_statement} SEL FEATURE_NAME FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where entity_name = '{entity_name}' AND DATA_DOMAIN = '{domain}'"

    # Executing the query and returning the result as a DataFrame
    return tdml.DataFrame.from_query(query)


def get_feature_versions(entity_name, features, domain=None, latest_version_only=True, version_lag=0):
    """
    Retrieve feature versions for specified features associated with certain entities
    from a given data domain. This function allows fetching either all versions or
    just the latest versions of the features.

    Parameters:
    entity_name (str or list): The name of the entity or a list of entity names
                               for which feature versions are to be fetched.
    features (list): A list of features for which versions are required.
    domain (str, optional): The data domain to filter the feature versions.
                            Defaults to None, where a predefined domain is used.
    latest_version_only (bool, optional): Flag to fetch only the latest version
                                          of each feature. Defaults to True.
    version_lag (int, optional): The number of versions to lag behind the latest.
                                 Only effective if latest_version_only is True. Defaults to 0.

    Returns:
    dict: A dictionary with feature names as keys and their corresponding versions as values.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Default to a predefined data domain if none is provided
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Convert the entity_name to a string if it is a list
    if type(entity_name) == list:
        entity_name = ','.join(entity_name)

    # Preparing the feature names for inclusion in the SQL query
    if type(features) == list:
        features = ["'" + f + "'" for f in features]
    else:
        features = "'" + features + "'"

    # Constructing the SQL query to fetch basic feature data for the specified entities and features
    query = f"""{validtime_statement}
    SEL FEATURE_ID, FEATURE_NAME, FEATURE_TABLE, FEATURE_DATABASE
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where entity_name = '{entity_name}' AND DATA_DOMAIN = '{domain}' 
    AND FEATURE_NAME in ({','.join(features)})"""

    # Executing the first query and converting the results to a pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # if df is empty
    if df.shape[0] == 0:
        print('the features you are requesting for this entity and data domain do not exist. Here is what you requested:')
        print('feature store database :', tdfs4ds.SCHEMA)
        print('feature catalog        :', tdfs4ds.FEATURE_CATALOG_NAME)
        print('entity name            :', entity_name)
        print('data domain            :', domain)
        print('features               :', ','.join(features))
        print('')
        print(query)
        return

    # Building the second query to fetch feature versions
    query = []
    for i, row in df.iterrows():
        query_ = f"""
        SEL DISTINCT A{i}.FEATURE_NAME, A{i}.FEATURE_VERSION
        FROM (
        {validtime_statement}
        SELECT CAST('{row['FEATURE_NAME']}' AS VARCHAR(255)) AS FEATURE_NAME, FEATURE_VERSION FROM {row['FEATURE_DATABASE']}.{row['FEATURE_TABLE']}
        WHERE FEATURE_ID = {row['FEATURE_ID']})
        A{i}
        """
        query.append(query_)

    # Combining the individual queries with UNION ALL
    query = '\n UNION ALL \n'.join(query)

    # Modifying the query to fetch only the latest versions, if specified
    if latest_version_only:
        query = 'SELECT * FROM (' + query + ') A \n' + f'QUALIFY ROW_NUMBER() OVER(PARTITION BY FEATURE_NAME ORDER BY FEATURE_VERSION DESC) = 1+{version_lag}'

    if tdfs4ds.DEBUG_MODE == True:
        print(query)
    # Executing the final query and converting the results to a pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # results in dictionary:
    results = {row['FEATURE_NAME']: row['FEATURE_VERSION'] for i, row in df.iterrows()}
    if tdfs4ds.DEBUG_MODE == True:
        print('---> RESULTS <---')
        print(results)
    # From the process catalog
    query = f"""
          SELECT 
            PROCESS_ID as FEATURE_VERSION,
            NGRAM AS FEATURE_NAME
          FROM NGramSplitter (
          ON (CURRENT VALIDTIME
            SELECT 
                PROCESS_ID ,
                FEATURE_NAMES 
            FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}
            WHERE DATA_DOMAIN = '{domain}') as paragraphs_input
          USING
          TextColumn ('FEATURE_NAMES')
          ConvertToLowerCase ('false')
          Grams ('1')
          Delimiter(',')
        ) AS dt   
        WHERE UPPER(FEATURE_NAME) in ({','.join([x.upper() for x in features])})
    """

    if tdfs4ds.DEBUG_MODE == True:
        print(query)

    # Executing the query:
    df = tdml.DataFrame.from_query(query).to_pandas()

    # results in dictionary:
    results2 = {row['FEATURE_NAME']: row['FEATURE_VERSION'] for i, row in df.iterrows()}

    if tdfs4ds.DEBUG_MODE == True:
        print('---> RESULTS <---')
        print(results2)

    results.update(results2)

    # Returning the results as a dictionary with feature names as keys and their versions as values
    return results
def get_entity_tables(entity_id, data_domain=None):
    """
    Retrieves a list of table names associated with a given entity ID or IDs from a feature catalog within a specific data domain.

    This function constructs and executes an SQL query to select distinct table names from a feature catalog that match the given entity ID(s) and data domain. If the data domain is not specified, it defaults to the system's default data domain. The entity ID can be a single string or a list of strings. If `DEBUG_MODE` is enabled in the system, the function prints the SQL query before execution.

    Parameters:
    - entity_id (str or list of str): The ID or IDs of the entities for which to retrieve table names.
    - data_domain (str, optional): The data domain within which to search for the entity IDs. Defaults to the system's default data domain if None.

    Returns:
    - list of str: A list of unique table names (in the format 'FEATURE_DATABASE.FEATURE_TABLE') associated with the given entity ID(s) within the specified data domain.

    Exceptions:
    - If the SQL query execution fails, the function attempts to retrieve the table names by converting the query results into a pandas DataFrame and then extracting the table names from it.

    Note:
    - This function depends on the external modules `tdfs4ds` and `tdml` for database schema details, default configurations, and SQL execution.
    """

    if data_domain is None:
        data_domain = tdfs4ds.DATA_DOMAIN

    if type(entity_id) == str:
        entity_id = [entity_id]

    query = f"""
    SELECT DISTINCT
    FEATURE_DATABASE || '.' || FEATURE_TABLE AS table_name
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
    WHERE ENTITY_NAME = '{','.join([k for k in entity_id])}'
    AND DATA_DOMAIN = '{data_domain}'
    """

    if tdfs4ds.DEBUG_MODE == True:
        print(query)

    try:
        table_list = [x[0] for x in tdml.execute_sql(query).fetchall()]
    except Exception as e:
        table_list = tdml.DataFrame.from_query(query).to_pandas().table_name.values

    return table_list

def get_feature_store_content(entity_id, data_domain=None, convert_to_date=False, time_manager = None, condition = '<='):
    """
    Retrieves content from a feature store for a given entity ID or IDs within a specified data domain, with options to convert datetime columns to dates, filter data based on a time management table, and apply a specific condition for the filter.

    This function first retrieves a list of table names associated with the given entity ID(s) in the specified data domain using the `get_entity_tables` function. It then constructs SQL queries to select distinct records from these tables, focusing on the 'ValidStart' column and the entity ID(s). If `convert_to_date` is True, it converts 'ValidStart' datetime values to date values in the queries. Additionally, if a `time_manager` object is provided, the function filters records in each table to include only those where 'ValidStart' meets the specified condition (e.g., before, on, or after) relative to the business date specified in the `time_manager`'s table. The condition for comparison is specified by the `condition` parameter.

    Parameters:
    - entity_id (str or list of str): The ID or IDs of the entities for which to retrieve content.
    - data_domain (str, optional): The data domain within which to search for the entity IDs. Defaults to the system's default data domain if None.
    - convert_to_date (bool, optional): Flag indicating whether to convert 'ValidStart' datetime values to date values. Defaults to False.
    - time_manager (object, optional): An object that specifies the schema and table name of a time management table to filter records based on business date. The object should have `schema_name` and `table_name` attributes, as well as a `data_type` indicating the type of data (e.g., date, datetime).
    - condition (str, optional): A string specifying the condition to apply to the 'ValidStart' column when filtering records based on the business date from the time management table. Defaults to '<='.

    Returns:
    - DataFrame: A DataFrame containing the retrieved content, with the 'ValidStart' column and the entity ID(s) from each table in the feature store that matches the criteria, optionally filtered by business date and specific condition.

    Note:
    - If `DEBUG_MODE` is enabled in the system, the function prints the constructed SQL query before execution.
    - This function leverages the `tdml` module for executing the SQL query and returning the results as a DataFrame.
    - The function adapts its behavior based on the presence and specifications of the `time_manager` object and the `condition` parameter to provide flexible data retrieval options.
    """
    if data_domain is None:
        data_domain = tdfs4ds.DATA_DOMAIN
    if type(entity_id) == str:
        entity_id = [entity_id]
    table_list = get_entity_tables(entity_id, data_domain)

    if time_manager is None:
        if convert_to_date:
            query = '\nUNION\n'.join(
                [f"SELECT DISTINCT CAST(ValidStart AS DATE) AS ValidStart, {','.join([k for k in entity_id])} FROM {x}" for x in table_list])
        else:
            query = '\nUNION\n'.join(
                [f"SELECT DISTINCT ValidStart, {','.join([k for k in entity_id])} FROM {x}" for x in table_list])
    else:
        if 'date' in time_manager.data_type.lower():
            if convert_to_date:
                query = '\nUNION\n'.join(
                    [f"SELECT DISTINCT CAST(ValidStart AS DATE) AS ValidStart, {','.join([k for k in entity_id])} FROM {x} WHERE CAST(ValidStart AS DATE) {condition} (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})" for x in table_list])
            else:
                query = '\nUNION\n'.join(
                    [f"SELECT DISTINCT ValidStart, {','.join([k for k in entity_id])} FROM {x} WHERE CAST(ValidStart AS DATE) {condition} (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})" for x in table_list])
        else:
            if convert_to_date:
                query = '\nUNION\n'.join(
                    [f"SELECT DISTINCT CAST(ValidStart AS DATE) AS ValidStart, {','.join([k for k in entity_id])} FROM {x} WHERE ValidStart {condition} (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})" for x in table_list])
            else:
                query = '\nUNION\n'.join(
                    [f"SELECT DISTINCT ValidStart, {','.join([k for k in entity_id])} FROM {x} WHERE ValidStart {condition} (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})" for x in table_list])

    if tdfs4ds.DEBUG_MODE == True:
        print(query)

    return tdml.DataFrame.from_query(query)