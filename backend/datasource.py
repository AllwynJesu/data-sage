from typing import List, Dict, Optional, Any
from dotenv import load_dotenv, find_dotenv
import os
import json
from atomic import AtomicLong

load_dotenv(find_dotenv())

data_sources_directory = os.getenv("DATASOURCE_DIR")

# Global atomic integer for tracking the last data source ID
last_data_source_id = AtomicLong(0)


def initialize_last_data_source_id():
    if not os.path.isdir(data_sources_directory):
        raise ValueError(
            f"Provided path '{data_sources_directory}' is not a valid directory."
        )

    max_id = 0
    for entry in os.scandir(data_sources_directory):
        if entry.is_dir() and entry.name.isdigit():
            max_id = max(max_id, int(entry.name))

    # Set the last_data_source_id atomically
    last_data_source_id.value = max_id


# Call initialization at the time of module load
initialize_last_data_source_id()


def get_all_datasources(fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    if not os.path.isdir(data_sources_directory):
        raise ValueError(
            f"Provided path '{data_sources_directory}' is not a valid directory."
        )

    # Default fields to return if none are specified
    fields = fields or ["id", "name"]

    result = []
    # Iterate through one-level subdirectories
    for entry in os.scandir(data_sources_directory):
        if entry.is_dir():  # Check if it's a subdirectory
            metadata_file_path = os.path.join(entry.path, "data_source_metadata.json")

            # Check if the metadata file exists
            if os.path.isfile(metadata_file_path):
                try:
                    with open(metadata_file_path, "r") as metadata_file:
                        data = json.load(metadata_file)

                    # Extract only the requested fields
                    extracted_data = {
                        field: data[field] for field in fields if field in data
                    }

                    # Add to the result if all requested fields are present
                    if len(extracted_data) == len(fields):
                        result.append(extracted_data)
                except (json.JSONDecodeError, IOError) as e:
                    # Handle invalid JSON or missing data gracefully
                    print(f"Skipping file '{metadata_file_path}' due to error: {e}")
    return result


def get_datasource_metadata_by_id(data_source_id: int) -> Dict[str, Any]:
    # Construct the directory path
    data_source_dir = os.path.join(data_sources_directory, str(data_source_id))

    # Validate the directory
    if not os.path.isdir(data_source_dir):
        raise ValueError(f"Data source directory '{data_source_dir}' does not exist.")

    # Path to the metadata file
    metadata_file_path = os.path.join(data_source_dir, "data_source_metadata.json")

    # Check if the metadata file exists
    if not os.path.isfile(metadata_file_path):
        raise FileNotFoundError(
            f"Metadata file not found for data source ID {data_source_id}."
        )

    # Read and parse the metadata file
    with open(metadata_file_path, "r") as metadata_file:
        metadata = json.load(metadata_file)

    return metadata


def store_datasource_metadata(new_data_source: Dict[str, Any]) -> None:
    if not isinstance(new_data_source, dict):
        raise ValueError("new_data_source must be a dictionary.")

    global last_data_source_id

    # Increment the atomic integer for the new data source ID
    last_data_source_id += 1
    data_source_id = last_data_source_id.value
    new_dir_name = str(data_source_id)
    new_data_source["id"] = data_source_id

    # Create the new directory
    new_dir_path = os.path.join(data_sources_directory, new_dir_name)
    os.makedirs(new_dir_path, exist_ok=True)

    # Path to the metadata file
    metadata_file_path = os.path.join(new_dir_path, "data_source_metadata.json")

    # Write the new data source metadata as JSON
    with open(metadata_file_path, "w") as metadata_file:
        json.dump(new_data_source, metadata_file, indent=4)

    print(f"New data source metadata stored in: {metadata_file_path}")


if __name__ == "__main__":
    new_metadata = {
        "host": "localhost",
        "port": 5432,
        "username": "user",
        "pwd": "password",
        "database": "example_db",
        "dialect": "postgresql",
        "name": "NewDataSource",
    }

    # store_datasource_metadata(new_metadata)
    print(get_all_datasources())
    print(get_datasource_metadata_by_id(1))
    print(get_datasource_metadata_by_id(5))
