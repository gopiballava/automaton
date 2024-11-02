from typing import Optional
from .models import Base, Item, Barcode, User, BarcodeType


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
    ) -> Item:
        new_barcode = Barcode(tag_value=tag_value, tag_type=tag_type)
        new_item = Item(title=title, description=description)
        new_item.barcodes.append(new_barcode)
        self._session.add(new_item)
        self._session.commit()
        return new_item
