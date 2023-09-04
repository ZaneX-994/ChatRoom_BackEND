import os
from pathlib import Path

from src.data_store import create_default_db, data_store


def clear_v1():
    """
    Resets the data store to a blank state.
    """
    db = create_default_db()
    data_store.set(db)

    # Remove added images.
    images = Path("images")
    for name in os.listdir(images):
        if name == "default.jpg":
            continue
        os.remove(images / name)

