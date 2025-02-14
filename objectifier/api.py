from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from .models import (
    Base,
    Item,
    Barcode,
    User,
    BarcodeType,
    ItemRelationship,
    RelationshipType,
)


class Api:
    def __init__(self, session):
        self._session = session

    def get_item_for_tag(self, tag_value: str) -> Item:
        found_barcode = (
            self._session.query(Barcode).filter_by(tag_value=tag_value).first()
        )
        return found_barcode.item

    def add_tagged_item(
        self,
        tag_value: str,
        title: str,
        description: Optional[str] = None,
        tag_type: Optional[BarcodeType] = None,
        is_location: Optional[bool] = None,
    ) -> Item:
        new_barcode = Barcode(tag_value=tag_value, tag_type=tag_type)
        new_item = Item(title=title, description=description, is_location=is_location)
        new_item.barcodes.append(new_barcode)
        self._session.add(new_item)
        self._session.commit()
        return new_item

    def query_items(self, query_string: str) -> List[Item]:
        return list(self._session.query(Item).filter(Item.title.contains(query_string)))

    def update_item_with_tag(
        self,
        tag_value: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Item:
        """Update the title and/or description of an item based on the scanned barcode tag."""
        found_item = self.get_item_for_tag(tag_value)
        if title is not None:
            found_item.title = title
        if description is not None:
            found_item.description = description
        return found_item

    def store_tagged_item_at_tagged_location(
        self, item_tag_value: str, location_tag_value: str
    ):
        """Mark an item as currently stored at this location."""
        item = self.get_item_for_tag(item_tag_value)
        # print(f"====> Item with tag {item.barcodes[0].tag_value} / {item_tag_value} to be stored: {item}")
        location = self.get_item_for_tag(location_tag_value)

        relat = ItemRelationship(
            from_item=item,
            to_item=location,
            relationship_type=RelationshipType.is_located_at,
        )
        self._session.add(relat)
        # assert location.is_location
        # item.stored_at_location = location
        try:
            self._session.commit()
        except IntegrityError:
            # Looks like we already have this item present; let's just silently accept this.
            self._session.rollback()

    def get_items_at_tagged_location(self, tag_value: str, include_container_contents: bool=False) -> List[Item]:
        """Find all items that are stored in this location."""
        location = self.get_item_for_tag(tag_value)
        retv = []
        for relationship in self._session.query(ItemRelationship).filter(
            ItemRelationship.to_item == location,
            ItemRelationship.relationship_type == RelationshipType.is_located_at,
        ):
            retv.append(relationship.from_item)
        if include_container_contents:
            raise NotImplementedError("We can't yet gather container contents.")
        return retv

