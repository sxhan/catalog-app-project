import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from item_catalog.models import Base, Category, Item
from item_catalog.auth import create_user
from start_app import app

engine = create_engine(app.config["DB_STRING"])
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Delete everything in db and restart from scratch
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


# Helper Functions
def add_rows(filepath, model):
    rows = json.load(open(filepath, 'rb'))
    for row in rows:
        new = model(**row)
        session.add(new)
        session.commit()

# Create users
user_data = json.load(open("data/user.json"))[0]
root = create_user(username=user_data["username"],
                   password=user_data["password"],
                   email=user_data["email"],
                   isoauth=user_data["isoauth"])

add_rows("data/category.json", Category)
add_rows("data/item.json", Item)
