import logging
import os
import uuid


def get_uuid() -> str:
    return str(uuid.uuid4())


def delete_file(file_path: str) -> None:
    try:
        os.remove(file_path)
        logging.info(f"Successfully deleted file: {file_path}")
    except Exception as e:
        logging.error(f"Error deleting file: {e}")
