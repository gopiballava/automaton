# import couchdb
# from sqlalchemy.orm import sessionmaker
from invoke import task
from objectifier.models import Base, MigratedCouchRecord
from sqlalchemy import create_engine
from objectifier.api import Api
from objectifier.couch_import import CouchImport
import os

if 'OBJECTIFIER_DATABASE' in os.environ:
    OBJECTIFIER_DATABASE = os.path.normpath(os.environ["OBJECTIFIER_DATABASE"])


def make_engine():
    engine = create_engine(f"sqlite:///{OBJECTIFIER_DATABASE}", echo=False)
    return engine


def make_session():
    engine = make_engine()
    Session = sessionmaker(engine)
    session = Session()
    return session


@task
def copy_from_couch(ctx):
    session = make_session()
    api = Api(session)

    PASSWORD = os.environ["COUCHDB_PASSWD"]
    couch = couchdb.Server(f"http://gopiballava:{PASSWORD}@localhost:5984/")
    db = couch["basedb"]

    ci = CouchImport(api, db)
    i = 0
    failed = 0
    for id in ci._db:
        if not ci.transfer_record(id, ci._db[id]):
            failed += 1
        i += 1
        print(f"======> ITEM COUNT {i} FAIL COUNT {failed}")
        # if i > 100:
        #     break
    print(f"======> ITEM COUNT {i} FAIL COUNT {failed}")
    session.commit()
    session.close()


@task
def translate_couch(ctx):
    print("hi")
    db_session = make_session()
    migrated_records = db_session.query(MigratedCouchRecord).where(
        MigratedCouchRecord.type == "barcode"
    )
    api = Api(db_session)
    ci = CouchImport(api)
    for record in migrated_records:
        ci.process_record(record.contents)
    print(len(list(migrated_records)))


@task
def list_barcodes(ctx):
    db_session = make_session()
    migrated_records = db_session.query(MigratedCouchRecord).where(
        MigratedCouchRecord.type == "barcode"
    )
    for record in migrated_records:
        print(record.contents.get("barcode_tag"))
    print(len(list(migrated_records)))


@task
def init_db(ctx):
    engine = make_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    session.commit()
    session.close()


@task
def find_item(ctx, search: str):
    session = make_session()
    api = Api(session)
    for item in api.query_items(search):
        print(item.single_line())


@task
def list_barcodes(ctx):
    db_session = make_session()
    migrated_records = db_session.query(MigratedCouchRecord).where(
        MigratedCouchRecord.type == "barcode"
    )
    barcodes = []
    for record in migrated_records:
        if "barcode_tag" in record.contents:
            barcodes.append(record.contents.get("barcode_tag", "***"))
        else:
            print(f"No tag found in {record.contents}")
    # barcodes = ["00", "01", "02", "10", "11"]
    barcodes.sort()
    print(f"Found {len(barcodes)} different codes")
    start_code = barcodes.pop(0)
    end_code = start_code
    for barcode in barcodes:
        try:
            int_code = int(barcode)
            if int(end_code) + 1 == int_code:
                end_code = barcode
            else:
                print(f"{start_code} - {end_code}")
                start_code = barcode
                end_code = barcode
        except ValueError:
            print(f"{start_code} - {end_code}") # Works because numbers come first :)
            print(barcode)
    # print(barcodes)
# 0000 - 0643
# 010513 - 010513
# 6aaa
# 6aab
# 6aac
# 6aad
# 6aae
# X0040O1S1N
# X0042HEZ7H
# abe
# dei
# del
# eaf
# eed
# qr2025
# qr3025
# qwe
##################
# TRUCK BAR CODES
# 02001
