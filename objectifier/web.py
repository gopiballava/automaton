from typing import List, Optional
from .api import Api
import cherrypy
from jinja2 import Environment, FileSystemLoader
from .models import Base, Item, Barcode, User, BarcodeType, StoredMisc

env = Environment(loader=FileSystemLoader("objectifier/templates"))


def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///test.sqlite?check_same_thread=False", echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def with_items(db_session) -> List[Item]:
    items = []
    for title, tag_value in (("OneItem", "abcd"), ("SecondItem", "defg")):
        valid_item = Item(
            title=title, description=f"Sample item for unit test: {title}"
        )
        db_session.add(valid_item)
        db_session.commit()
        barcode = Barcode(tag_value=tag_value)
        valid_item.barcodes.append(barcode)
        items.append(valid_item)
    db_session.commit()
    print(f"Created: {items}")
    return items


class RootWeb:
    def __init__(self):
        self._session = next(db_session())
        # with_items(self._session)
        self._api = Api(self._session)

    @cherrypy.expose
    def index(self):
        tmpl = env.get_template("index.html")
        return tmpl.render(salutation="Hello", target="World")

    @cherrypy.expose
    def list(self):
        item_list = self._api.query_items("")
        tmpl = env.get_template("list.html")
        return tmpl.render(data=item_list)

    @cherrypy.expose
    def item_detail(self, item_id: Optional[str] = None):
        tmpl = env.get_template("item_detail.html")
        if item_id:
            item = self._api.get_item_with_id(item_id=item_id)
            if item is None:
                raise RuntimeError(f"Could not find item with id {item_id}")
            return tmpl.render(
                button_text="Update",
                title=item.title,
                description=item.description,
                item_id=item_id,
            )
        return tmpl.render(
            button_text="Create",
        )

    @cherrypy.expose
    def item_detail_update(self, title=None, description=None, tag=None, item_id: Optional[str] = None):
        # if tag is "":
        #     tag = None
        # if title is "":
        #     title = None
        
        if item_id:
            item = self._api.get_item_with_id(item_id=item_id)
            if item is None:
                raise RuntimeError(f"Could not find item with id {item_id}")
            item.title = title
            item.description = description
            print(f"=====> UPDATED with {item}")
        else:
            self._api.add_tagged_item(tag_value=tag, title=title, description=description)
        raise cherrypy.HTTPRedirect("/list")


def quickstart():
    cherrypy.quickstart(RootWeb(), "/")
