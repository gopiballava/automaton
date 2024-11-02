from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Item, Barcode, User, BarcodeType, StoredMisc
import pytest
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


@pytest.fixture(scope="function")
def with_items(db_session) -> List[Item]:
    items = []
    for (title, tag_value) in (("OneItem", "abcd"), ("SecondItem", "defg")):
        valid_item = Item(title=title, description=f"Sample item for unit test: {title}")
        db_session.add(valid_item)
        db_session.commit()
        barcode = Barcode(tag_value=tag_value)
        valid_item.barcodes.append(barcode)
        items.append(valid_item)
    db_session.commit()
    return items


class TestCoreAPI:
    def test_item_retrieval(self, api: Api, with_items):
        retrieved_item = api.get_item_for_tag("abcd")
        assert retrieved_item == with_items[0]

    def test_tagged_item_adder(self, api: Api):
        new_item = api.add_tagged_item(tag_value="newqr", title="newly_added_item")
        retrieved_item = api.get_item_for_tag("newqr")
        assert retrieved_item.title == "newly_added_item"
