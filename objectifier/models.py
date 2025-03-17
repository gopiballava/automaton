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
        back_populates="is_related_to",
        foreign_keys=[from_id],
    )
    to_item: Mapped["Item"] = relationship(
        back_populates="is_related_from",
        foreign_keys=[to_id],
    )
    def __repr__(self) -> str:
        return f"ItemRelationship(from_id={self.from_id}, to_id={self.to_id})"


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]

    barcodes: Mapped[List["Barcode"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
    def tag_values(self) -> List[str]:
        return [barcode.tag_value for barcode in self.barcodes]
    # item_description: Mapped["ItemDescription"] = relationship(back_populates="item", cascade="all, delete-orphan")

    is_related_to: Mapped[List["ItemRelationship"]] = relationship(
        # secondary="item_relationship_table"
        # primaryjoin=lambda: Item.id == ItemRelationship.to_id
        # primaryjoin="Item.id == ItemRelationship.to_id"
        back_populates="from_item",
        foreign_keys=[ItemRelationship.from_id],
    )

    is_related_from: Mapped[List["ItemRelationship"]] = relationship(
        # secondary="item_relationship_table"
        # primaryjoin=lambda: Item.id == ItemRelationship.to_id
        # primaryjoin="Item.id == ItemRelationship.to_id"
        back_populates="to_item",
        foreign_keys=[ItemRelationship.to_id],
    )

    is_location: Mapped[bool] = False
    is_container: Mapped[bool] = False

    def stored_at_location(self):
        for elem in self.is_related_to:
            if elem.relationship_type == RelationshipType.is_located_at:
                print(f"=====> stored_at_location: {elem}")
                return elem.to_item
        return None
    
    def items_stored_here(self):
        return [item for item in self.is_related_from if item.relationship_type == RelationshipType.is_located_at]
    
    def store_item_here(self, item):
        if item not in self.items_stored_here():
            print(f"=======> store;  item.id: {item.id} self.id(basement): {self.id}")
            # rel = ItemRelationship(from_id=item.id, to_id=self.id, relationship_type=RelationshipType.is_located_at)
            rel = ItemRelationship(relationship_type=RelationshipType.is_located_at)
            print(f"======> rel.from: {rel.from_id} rel.to_id: {rel.to_id}")
            item.is_related_to.append(rel)
            self.is_related_from.append(rel)
            print(f"======> rel.from: {rel.from_id} rel.to_id: {rel.to_id}")
            return rel

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, title={self.title!r}, description={self.description!r})"
    
    def single_line(self) -> str:
        return f"{self.id!r}  {self.title!r}  {self.description!r}"


# class ItemDescription(Base):
#     __tablename__ = "item_descriptions"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
#     item: Mapped["Item"] = relationship(back_populates="item_description")

#     title: Mapped[str]
#     description: Mapped[Optional[str]]
#     notes: Mapped[Optional[str]]

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
