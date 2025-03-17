from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Item, Barcode, User, BarcodeType, StoredMisc, ItemRelationship, RelationshipType
import pytest


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    # session.configure(engine=engine)
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def valid_user():
    valid_user = User(
        name="Ezzeddin", fullname="Ezzeddin Aybak", email="aybak_email@gmail.com"
    )
    return valid_user


@pytest.fixture(scope="function")
def with_item(db_session):
    valid_item = Item(title="OneItem", description="Sample item for unit test")
    db_session.add(valid_item)
    db_session.commit()
    return valid_item


@pytest.fixture(scope="function")
def db_session_with_users(db_session, valid_user):
    db_session.add(valid_user)
    db_session.commit()
    yield db_session


class TestBarcodes:
    def test_barcode_relationship(self, db_session, with_item: Item):
        barcode = Barcode(tag_value="abcd")
        assert len(with_item.barcodes) == 0
        with_item.barcodes.append(barcode)
        db_session.commit()
        assert len(with_item.barcodes) == 1
        barcode_b = Barcode(tag_value="abcde")
        with_item.barcodes.append(barcode_b)
        db_session.commit()
        assert len(with_item.barcodes) == 2

        found_barcode = db_session.query(Barcode).filter_by(tag_value="abcd").first()
        assert found_barcode.item == with_item
        print(f"=====> type: {found_barcode.tag_type}")
        found_barcode.tag_type = BarcodeType.qr_code
        print(f"=====> type: {found_barcode.tag_type}")
        print(f"=====> found barcode: {found_barcode}")
        # assert False

    @pytest.mark.xfail(raises=IntegrityError)
    def test_barcode_unique(self, db_session, with_item: Item):
        barcode = Barcode(tag_value="abcd")
        assert len(with_item.barcodes) == 0
        with_item.barcodes.append(barcode)
        db_session.commit()
        assert len(with_item.barcodes) == 1
        barcode_b = Barcode(tag_value="abcd")
        with_item.barcodes.append(barcode_b)
        db_session.commit()

    def test_location(self, db_session, with_item: Item):
        assert with_item.stored_at_location() == None
        # assert len(with_item.location_contains_items) == 0
        basement = Item(title="Basement")
        db_session.add(basement)
        db_session.commit()
        assert len(basement.items_stored_here()) == 0
        
        rel = basement.store_item_here(with_item)
        # assert len(with_item.location_contains_items) == 1
        # assert len(with_item.is_related_to) == 1
        found_item = db_session.query(Item).filter_by(title="OneItem").first()
        assert len(found_item.is_related_to) == 1
        # print(f"=====> stored_at from_id: {found_item.stored_at_location().from_id} to_id: {found_item.stored_at_location().to_id}")
        assert found_item.stored_at_location().title == "Basement"
        assert found_item.stored_at_location().id == basement.id
        assert len(basement.items_stored_here()) == 1

    def test_json(self, db_session):
        misc = StoredMisc(item_key="unit_test", value={"foo": "bar"})
        db_session.add(misc)
        db_session.commit()
        # This should automatically update the database:
        misc.value["foo"] = "barbar"
        data = db_session.query(StoredMisc).filter_by(item_key="unit_test").first()
        assert data.value == {"foo": "barbar"}
    
    # def test_relationships(self, db_session):
    #     basement = Item(title="Basement")
    #     epoxy = Item(title="epoxy")
    #     assert len(epoxy.is_related_to) == 0
    #     assert len(basement.is_related_to) == 0
    #     relate = ItemRelationship(relationship_type=RelationshipType.is_located_at)
    #     relate.to_item = epoxy
    #     relate.from_item = basement
    #     assert len(epoxy.is_related_to) == 1
    #     assert len(basement.is_related_from) == 1

    #     assert len(epoxy.is_related_from) == 0
    #     assert len(basement.is_related_to) == 0
    #     db_session.commit()
    #     assert len(epoxy.is_related_to) == 1
    #     assert len(basement.is_related_to) == 0


class TestBlog:
    def test_author_valid(self, db_session, valid_user):
        db_session.add(valid_user)
        db_session.add(valid_user)
        db_session.commit()
        all = db_session.query(User).filter_by(name="Ezzeddin").all()
        assert len(all) == 1
        # aybak = db_session.query(User).filter_by(name="Ezzeddin").first()
        # assert "Ezzeddin" in aybak.fullname
        # assert "Abdullah" not in aybak.fullname
        # assert aybak.email == "aybak_email@gmail.com"

    def test_author_exists(self, db_session_with_users):
        aybak = db_session_with_users.query(User).filter_by(name="Ezzeddin").first()
        assert "Ezzeddin" in aybak.fullname
        assert "Abdullah" not in aybak.fullname
        assert aybak.email == "aybak_email@gmail.com"

    def test_author_unique(self, db_session_with_users):
        all = db_session_with_users.query(User).filter_by(name="Ezzeddin").all()
        assert len(all) == 1

    def test_author_unique_b(self, db_session_with_users):
        all = db_session_with_users.query(User).filter_by(name="Ezzeddin").all()
        assert len(all) == 1
