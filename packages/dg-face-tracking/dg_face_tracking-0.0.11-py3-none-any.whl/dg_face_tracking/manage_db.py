import os
import sys

from pathlib import Path
Path(__file__).resolve()

from .Database.vectstore import VectStore


def list_embeds_db(path):
    db = None
    try:
        db = VectStore.load(path)
        entries = db.list_entries()
        if len(entries) > 0:
            for entry in entries:
                print(entry)
        else:
            print(f"{path} is empty")
    except FileNotFoundError as e:
        print(e)


def delete_entry_db(path, entry):
    db = None
    try:
        db = VectStore.load(path)
        if db.del_entry(entry):
            db.dump(path)
            print(f"Successfully deleted: {entry}")
        else:
            print(f"No such entry: {entry}")
    except FileNotFoundError as e:
        print(e)




