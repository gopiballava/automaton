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

    def test_item_query(self, api: Api, with_items):
        assert len(api.query_items("Item")) == 2
        assert len(api.query_items("item")) == 2
        assert len(api.query_items("OneItem")) == 1
        assert len(api.query_items("One")) == 1
        assert len(api.query_items("items")) == 0

    def test_stored_at_location(self, api: Api, with_items: List[Item]):
        location_tag = "qr_location"
        new_location = api.add_tagged_item(tag_value=location_tag, title="newly_added_location", is_location=True)
        assert len(api.get_items_at_tagged_location(location_tag)) == 0
        api.store_tagged_item_at_tagged_location("abcd", location_tag)
        assert len(api.get_items_at_tagged_location(location_tag)) == 1
        # Add a second item:
        api.store_tagged_item_at_tagged_location(with_items[1].barcodes[0].tag_value, location_tag)
        assert len(api.get_items_at_tagged_location(location_tag)) == 2
        # Add the first item a second time:
        api.store_tagged_item_at_tagged_location(with_items[0].barcodes[0].tag_value, location_tag)
        assert len(api.get_items_at_tagged_location(location_tag)) == 2

    # def test_stored_at_location_low_level(self, api: Api, with_items: List[Item]):
    #     new_location = api.add_tagged_item(tag_value="newqr", title="newly_added_location", is_location=True)
    #     new_location = api.get_item_for_tag("newqr")
    #     assert len(new_location.location_contains_items) == 0
    #     with_items[0] = api.get_item_for_tag("abcd")
    #     with_items[0].stored_at_location = new_location
    #     assert len(new_location.location_contains_items) == 1
    #     assert len(api.get_items_at_tagged_location('newqr')) == 1
    #     print(f"=====> Items from call: {new_location.location_contains_items}")
    #     print(f"=====> Items from call as LIST: {list(new_location.location_contains_items)}")
    #     print(f"=====> Items from API: {api.get_items_at_tagged_location('newqr')}")
    #     # assert False


