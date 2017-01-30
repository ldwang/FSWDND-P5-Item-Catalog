from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
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


#create users
User1 = User(name="Udacity", email="support@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Item for snowboarding
category1 = Category(user_id=1, name="Snowboarding")

session.add(category1)
session.commit()


item1 = Item(name="Snowboard", description="Best for any terrain and conditions. All-mountain snowboards perform anywhere on a mountain-groo,ed runs, backcountry, even park and pipe.",
                     category = category1, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Goggles", description="Used for protecting the snow blind. ",
                     category=category1, user=User1)

session.add(item2)
session.commit()

#Item for Soccer
category2 = Category(user_id=1, name="Soccer")

session.add(category2)
session.commit()


item1 = Item(name="Soccer Cleats", description="With a tough construction for enhanced durability, Nike Mercurial Veer Football is perfect for both practice and performance. Designed for speed, its 26-panel design provides the right touch to accelerate your performance.",
                     category = category2, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Soccer Balls", description="With a tough construction for enhanced durability, Nike Mercurial Veer Football is perfect for both practice and performance. Designed for speed, its 26-panel design provides the right touch to accelerate your performance.",
                     category=category2, user=User1)

session.add(item2)
session.commit()

item3 = Item(name="Goalkeeper Gloves", description="Give yourself every advantage with these junior soccer goalkeeper gloves. Super-soft palms and maximum grip make the difference in making crucial saves. The FINGERSAVE build stiffens fingers to maximize ball deflection, and a negative-cut design provides a snug fit.",
                     category=category2, user=User1)

session.add(item3)
session.commit()

#Item for Soccer
category3 = Category(user_id=1, name="Basketball")

session.add(category3)
session.commit()

item1 = Item(name="Basketball Hoops", description="This basketball system features a steel-framed, shatter-proof backboard with a blow-molded frame pad for maximum durability. Power Lift construction allows for effortless height adjustments, while the XL heavy-duty portable base and straight round extension arms provide extra stability.",
                     category = category3, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Basketball Shoes", description="Get your young athlete in gear with the Under Armour Jet basketball shoe. Constructed with lightweight leather material, the upper remains durable and breathable when the action heats up. Synthetic overlays increase lateral and medial support, while the padded collar improves ankle comfort. A full-length EVA sockliner adds an extra layer of padding, ensuring they stay comfortable during wear. A one-piece rubber outsole improves grip.",
                     category=category3, user=User1)

session.add(item2)
session.commit()

print "added category items!"
