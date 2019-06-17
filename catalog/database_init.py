from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from database_setup import *

engine = create_engine("sqlite:///handbags.db")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Drop all tables
Base.metadata.drop_all()

# Recreate tables
Base.metadata.create_all()
# session.query(Owner).delete()

# session.query(Category).delete()

# session.query(Item_Details).delete()

# Create Owner
admin1 = Admin(admin_name="Sravanthi",
               admin_email="sravanthi7.b@gmail.com",
               admin_picture="http://anahitahashemzade.ir/wp-content/uploads/2018/12/ana-12-797x1024.jpg")
session.add(admin1)
session.commit()
print("Done..!")

# Create Categories

category1 = Category(name="JuteHandbags", admin_id=1)
session.add(category1)
session.commit()

category2 = Category(name="FancyHandbags", admin_id=1)
session.add(category2)
session.commit()

category3 = Category(name="TotesBags", admin_id=1)
session.add(category3)
session.commit()

category4 = Category(name="SlingHandbags", admin_id=1)
session.add(category4)
session.commit()


# Item_Details
item1 = Product_Details(brandname="jute Cottage",
                        material="jute",
                        picture="https://i.ebayimg.com/images/g/IucAAOSwstxVMlx6/s-l300.jpg",
                        color="multi colored handbag",
                        price="1000",
                        description="Jutebag is one of the most affordable natural fibers",
                        category_id="1",
                        adminid=1)
session.add(item1)
session.commit()

item2 =Product_Details(brandname="Alessia",
                        material="synthetic",
                        picture="https://financesonline.com/uploads/2014/07/hand.jpg",
                        color="Sand Color",
                        price="5000",
                        description="Attractive Looks with Enough space",
                        category_id="2",
                        adminid=1)
session.add(item2)
session.commit()

item3 = Product_Details(brandname="Lavie",
                        material="Polyster",
                        picture="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrkfQDzsM9rtevO0ZcC7lu8-6efCzG29eb7SA8jiEGcn2upCtp",
                        color="Skyblue",
                        price="900",
                        description="Capacity & Pockets: 1 Compartment",
                        category_id="3",
                        adminid=1)
session.add(item3)
session.commit()

item4 = Product_Details(brandname="Call it Spring",
                        material="Velvet",
                        picture="https://a.1stdibscdn.com/archivesE/upload/1121189/v_45772411531550693379/4577241_master.jpg?width=768",
                        color="Red",
                        price="600",
                        description="A stunning vintage handmade sling bag",
                        category_id="4",
                        adminid=1)
session.add(item4)
session.commit()

print("Products are Added..!")
