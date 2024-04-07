import csv
from typing import Iterable, Any, Union, List, Dict, Optional

def generate_from_dict(data: Union[Dict[str, Any], List[Dict[str, Any]]], output_path: str, headers: Optional[List[str]] = None):
    """
    Generate a CSV file from a dictionary or a list of dictionaries.

    Args:
        data (Union[Dict[str, Any], List[Dict[str, Any]]]): A dictionary or a list of dictionaries containing the data.
        output_path (str): The file path for the output CSV file.
        headers (Optional[List[str]]): An optional list of headers to use for the CSV file.
            If not provided, the keys from the first dictionary in the data will be used.

    Raises:
        ValueError: If the data is not a dictionary or a list of dictionaries.
    """
    if isinstance(data, dict):
        data = [data]

    if not all(isinstance(item, dict) for item in data):
        raise ValueError("Data must be a dictionary or a list of dictionaries.")

    rows = []
    if headers is None:
        headers = list(data[0].keys())
    rows.append(headers)

    for item in data:
        row = [item.get(header, '') for header in headers]
        rows.append(row)

    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def generate_from_db(query: str, db_connection, output_path: str, headers: Optional[List[str]] = None):
    """
    Generate a CSV file from a database query.

    Args:
        query (str): The SQL query to execute.
        db_connection: The database connection object.
        output_path (str): The file path for the output CSV file.
        headers (Optional[List[str]]): An optional list of headers to use for the CSV file.
            If not provided, the column names from the query result will be used.

    Raises:
        ValueError: If the database connection or the query result is invalid.
    """
    try:
        cursor = db_connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        raise ValueError(f"Error executing the query: {e}")

    if not rows:
        raise ValueError("Query returned no results.")

    if headers is None:
        headers = [desc[0] for desc in cursor.description]

    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    cursor.close()