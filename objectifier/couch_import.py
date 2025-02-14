from sqlalchemy.exc import IntegrityError, InterfaceError
import traceback
import couchdb
import os
from .api import Api
from .models import MigratedCouchRecord


PASSWORD = os.environ.get("COUCHDB_PASSWD", None)


class CouchImport:
    def __init__(self, api: Api, db = None):
        self._api = api
        self._db = db

    def transfer_record(self, record_id: str, record_dict: dict) -> bool:
        """Copies record_dict, from couchdb, to our internal clone."""
        try:
            migrated = MigratedCouchRecord(
                id=record_id, type=record_dict["$type"], contents=dict(record_dict)
            )
            self._api._session.add(migrated)
        except:
            traceback.print_exc()
            return False
        return True

    def process_record(self, record_dict) -> bool:
        if record_dict.get("$type") == "barcode":
            return self._process_barcode_record(record_dict)
        elif record_dict.get("$type") == "item":
            return self._process_item_record(record_dict)

    def _process_barcode_record(self, barcode_dict) -> bool:
        if barcode_dict["attached_item_id"] is None:
            print(f"Attached item is NONE for barcode object: {barcode_dict}")
            return
        try:
            # couch_item = self._db[barcode_dict["attached_item_id"]]
            couch_item = (
                self._api._session.query(MigratedCouchRecord)
                .where(MigratedCouchRecord.id == barcode_dict["attached_item_id"])
                .first()
                .contents
            )
        except couchdb.http.ResourceNotFound:
            print(f"======> Resource not found for barcode object: {barcode_dict}")
            return
        except TypeError:
            print(f"=====> TypeError with barcode object: {barcode_dict}")
            return
        except:
            traceback.print_exc()
            print(f"=====> OTHER error with barcode object: {barcode_dict}")
            return

        try:
            self._api.add_tagged_item(
                tag_value=barcode_dict["barcode_tag"],
                title=couch_item["title"],
                description=couch_item.get("subtitle", None),
                is_location=couch_item["item_subtype"] == "location",
            )
        except IntegrityError:
            print(f"Integrity error adding tag {barcode_dict['barcode_tag']}")
            self._api._session.rollback()
        except KeyError:
            traceback.print_exc()
            print(f"Error with record {couch_item}")
            self._api._session.rollback()
        return True
        

    def _process_item_record(self, record_dict) -> bool:
        print(record_dict)
        return True
