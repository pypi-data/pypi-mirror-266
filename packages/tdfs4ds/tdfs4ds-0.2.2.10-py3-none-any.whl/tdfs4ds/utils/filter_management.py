import teradataml as tdml
import tdfs4ds



def get_hidden_table_name(table_name):
    return table_name + '_HIDDEN'


class FilterManager:
    """
    Manages dynamic filtering on a database table by creating and managing a view based on filter criteria.

    This class is designed to facilitate the management of filtered views on a database table, allowing for dynamic selection of data based on filter criteria. It handles the creation and update of a filtered view based on a specified filter ID, supporting operations like loading new filters, updating existing filters, and dropping the filter view if necessary.

    Attributes:
        schema_name (str): Name of the schema in the database where the table and view are located.
        table_name (str): Name of the underlying table in the schema that holds the data to be filtered.
        view_name (str): Name of the view to be created or managed, which will present filtered data.
        filter_id_name (str): The column name used to identify different filters. Defaults to 'filter_id'.
        nb_filters (int): The number of filters currently defined in the table. This is updated when filters are loaded or modified.
    """

    def __init__(self, table_name, schema_name, filter_id_name='filter_id'):
        """
        Initializes the FilterManager with names for the table, schema, and an optional name for the filter ID column.

        Upon initialization, it checks if the specified table exists; if so, it sets up the necessary attributes including the current number of filters. If the table does not exist, the initialization process includes provisions for table creation.

        Args:
            table_name (str): Name of the table to manage filters for.
            schema_name (str): Name of the schema where the table is located.
            filter_id_name (str, optional): The name of the column used to identify filters. Defaults to 'filter_id'.
        """
        self.schema_name = schema_name
        self.table_name = get_hidden_table_name(table_name)
        self.view_name = table_name
        self.filter_id_name = filter_id_name
        self.nb_filters = None
        self.col_names = None
        if self._exists():
            df = tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))
            self.filter_id_name = df.columns[0]
            self.col_names = df.columns[1::]
            self.nb_filters = tdml.execute_sql(
                f"SEL MAX({self.filter_id_name}) AS nb_filters FROM {self.schema_name}.{self.table_name}").fetchall()[
                0][0]

    def load_filter(self, df):
        """
        Loads a new filter into the table and updates the view to reflect this filter.

        This method takes a DataFrame as input, assigns filter IDs to each row, and updates or replaces the table and view to reflect the new filter configuration.

        Args:
            df (DataFrame): The data containing the new filter configuration.
        """
        self.col_names = df.columns
        col_names = ', '.join(self.col_names)
        df_filter = df.assign(**{self.filter_id_name: tdml.sqlalchemy.literal_column(
            f"ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY {col_names})", tdml.BIGINT())})[['filter_id'] + df.columns]
        df_filter.to_sql(table_name=self.table_name, schema_name=self.schema_name, if_exists='replace')

        col_names = ', \n'.join(self.col_names)

        query = f"""
        REPLACE VIEW {self.schema_name}.{self.view_name} AS
        SEL {col_names}
        FROM {self.schema_name}.{self.table_name}
        WHERE {self.filter_id_name} = 1
        """

        tdml.execute_sql(query)

        self.nb_filters = tdml.execute_sql(
            f"SEL MAX({self.filter_id_name}) AS nb_filters FROM {self.schema_name}.{self.table_name}").fetchall()[0][0]

    def _exists(self):
        """
        Checks if the table associated with this FilterManager exists in the database.

        Returns:
            bool: True if the table exists, False otherwise.
        """

        return len([x for x in tdml.db_list_tables(schema_name=self.schema_name).TableName.values if
                    x.lower().replace('"', '') == self.view_name.lower()]) > 0

    def _drop(self):
        """
        Drops the view and the table from the database if they exist.

        This method is used to clean up the database by removing the managed view and table. It checks for the existence of the table and view before attempting to drop them.
        """
        # Drop the table if it exists
        if self._exists():
            tdml.db_drop_view(schema_name=self.schema_name, table_name=self.table_view)
            tdml.db_drop_table(schema_name=self.schema_name, table_name=self.table_name)

    def update(self, filter_id):
        """
        Updates the view to apply a new filter based on the provided filter ID.

        Args:
            filter_id (int): The ID of the filter to apply. The view will be updated to only show data that matches this filter ID.
        """
        if self._exists():
            query = f"""
            REPLACE VIEW {self.schema_name}.{self.view_name} AS
            SEL {','.join(self.col_names)}
            FROM {self.schema_name}.{self.table_name}
            WHERE {self.filter_id_name} = {filter_id}
            """

            if tdfs4ds.DEBUG_MODE:
                print(query)
            tdml.execute_sql(query)

    def display(self):
        """
        Retrieves the current data from the view as a DataFrame.

        Returns:
            DataFrame: The current data visible through the view, filtered by the active filter ID.
        """
        return tdml.DataFrame(tdml.in_schema(self.schema_name, self.view_name))

    def get_all_filters(self):
        return tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))