from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy_json import mutable_json_type
from typing import List, Set
from typing import Optional
import enum
from sqlalchemy import Integer, Enum, JSON
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class BarcodeType(enum.Enum):
    qr_code = "qr_code"
    datamatrix = "datamatrix"
    code128 = "code128"


# NOT USED right now.
class ItemType(enum.Enum):
    location = "location"


class RelationshipType(enum.Enum):
    is_located_at = "is_located_at"
    is_contained_inside = "is_contained_inside"
    belongs_inside_kit = "belongs_inside_kit"


class ItemRelationship(Base):
    __tablename__ = "item_relationship_table"
    # id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    to_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
    relationship_type: Mapped[RelationshipType]
    # from_item: Mapped["Item"] = relationship(foreign_keys=[from_id])
    from_item: Mapped["Item"] = relationship(
        back_populates="is_related_from",
        foreign_keys=[from_id],
    )
    to_item: Mapped["Item"] = relationship(
        back_populates="is_related_to",
        foreign_keys=[to_id],
    )


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    barcodes: Mapped[List["Barcode"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )

    is_related_to: Mapped[List["ItemRelationship"]] = relationship(
        # secondary="item_relationship_table"
        # primaryjoin=lambda: Item.id == ItemRelationship.to_id
        # primaryjoin="Item.id == ItemRelationship.to_id"
        back_populates="to_item",
        foreign_keys=[ItemRelationship.to_id],
    )

    is_related_from: Mapped[List["ItemRelationship"]] = relationship(
        # secondary="item_relationship_table"
        # primaryjoin=lambda: Item.id == ItemRelationship.to_id
        # primaryjoin="Item.id == ItemRelationship.to_id"
        back_populates="from_item",
        foreign_keys=[ItemRelationship.from_id],
    )

    is_location: Mapped[bool] = False
    stored_at_location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("items.id"))
    stored_at_location = relationship(
        "Item",
        back_populates="location_contains_items",
        remote_side=[id],
        foreign_keys=[stored_at_location_id],
    )
    location_contains_items: Mapped[Set["Item"]] = relationship(
        back_populates="stored_at_location", foreign_keys=[stored_at_location_id]
    )

    is_container: Mapped[bool] = False
    stored_in_container_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("items.id")
    )
    stored_in_container = relationship(
        "Item",
        back_populates="container_contains_items",
        remote_side=[id],
        foreign_keys=[stored_in_container_id],
    )
    container_contains_items: Mapped[Set["Item"]] = relationship(
        back_populates="stored_in_container",
        foreign_keys=[stored_in_container_id],
    )

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, title={self.title!r}, description={self.description!r})"
    
    def single_line(self) -> str:
        return f"{self.id!r}  {self.title!r}  {self.description!r}"


class Barcode(Base):
    __tablename__ = "barcodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag_value: Mapped[str] = mapped_column(unique=True)
    tag_type: Mapped[Optional[BarcodeType]]
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    item: Mapped["Item"] = relationship(back_populates="barcodes")

    def __repr__(self) -> str:
        return str(self.__dict__)
        # return f"Barcode(id={self.id!r}, tag_value={self.tag_value!r})"


class StoredMisc(Base):
    __tablename__ = "stored_misc"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_key: Mapped[str] = mapped_column(unique=True)
    value: Mapped[dict] = mapped_column(mutable_json_type(dbtype=JSON, nested=True))
    # = Column(mutable_json_type(dbtype=JSONB, nested=True))


class MigratedCouchRecord(Base):
    __tablename__ = "migrated_couch_record"
    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str]
    contents: Mapped[dict] = mapped_column(mutable_json_type(dbtype=JSON, nested=True))


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    email: Mapped[Optional[str]]  # REMOVFE this eventually.
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
