from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import pytest
from .couch_import import CouchImport
from .api import Api


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def api(db_session):
    return Api(db_session)


class TestImport:
    def test_couch_import(self, api: Api):
        ci = CouchImport(api)
        i = 0
        failed = 0
        for id in ci._db:
            if not ci.transfer_record(id,ci._db[id]):
                failed +=1 
            i += 1
            # if i > 100:
            #     break
        print(f"======> ITEM COUNT {i} FAIL COUNT {failed}")
        api._session.commit()
        # for qr in ["0093", "0094"]:
        #     item = api.get_item_for_tag(qr)
        #     print(f"{qr}: {item}")
        assert False
