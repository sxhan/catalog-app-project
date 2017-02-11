from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from item_catalog.models import Base, Category, Item, User
from item_catalog.auth import create_user
from start_app import app

engine = create_engine(app.config["DB_STRING"])
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete everything in db and restart from scratch
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


# Helper Functions

def add_category(name):
    category = Category(name=name)
    session.add(category)
    session.commit()
    return category


def add_item(name, description, category_id, user_id):
    item = Item(name=name, description=description,
                category_id=category_id, user_id=user_id)
    session.add(item)
    session.commit()
    return item


# Create users
root = create_user(
    username="root",
    password="$2b$12$j7qGIdT6gxEG1xLVexDn/.jJPQe3Eb/zAVKD8aaYp95FSBkVirjMG",
    email="root@root.root", isoauth=False)

# Create categories
soccer = add_category("Soccer")
bball = add_category("Basketball")
baseball = add_category("Baseball")
frisbee = add_category("Frisbee")
snowboarding = add_category("Snowboarding")
rock = add_category("Rock Climbing")
foosball = add_category("Foosball")
skating = add_category("Skating")
hockey = add_category("Hockey")

# Create Items
add_item("Snowboard", "Best for any terrain and conditions. All-mountain...",
         snowboarding.id, root.id)
add_item("Goggles", "Fun pair of trendy goggles!",
         snowboarding.id, root.id)
add_item("Stick", "Its brown and sticky",
         hockey.id, root.id)
add_item("Shinguards", "You'll never say 'Ow my shins' anymore.",
         soccer.id, root.id)
add_item("Frisbee", "You threw this at your dog once and it hit him in the "
         "face",
         frisbee.id, root.id)
add_item("Bat", "Not the kind that Ozzy Ate",
         baseball.id, root.id)
add_item("Jersey", "Shore",
         soccer.id, root.id)
add_item("Soccer cleats", "Its like wearing sonic on your feet",
         baseball.id, root.id)
