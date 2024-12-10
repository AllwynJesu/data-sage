from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

data_sources_directory = os.getenv("DATASOURCE_DIR")


def embedded_and_store_table_summary(
    data_source_id: int, table_name: str, table_summary: str
):
    data_source_dir = os.path.join(data_sources_directory, str(data_source_id))
    pass


def get_relevant_tables_for_given_query(data_source_id: int, user_query: str):
    pass
