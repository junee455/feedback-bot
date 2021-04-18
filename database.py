#!/usr/bin/python

import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import config 

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("no database name")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    
    
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    photo = sqlalchemy.Column(sqlalchemy.String)
    stars = sqlalchemy.Column(sqlalchemy.Integer)
    
    category = orm.relation('Category', back_populates="products")
    
    category_id = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("categories.id"))

    
# class User(SqlAlchemyBase):
#     __tablename__ = 'users'

#     id = sqlalchemy.Column(sqlalchemy.Integer,
#                            primary_key=True, autoincrement=True)

#     user_id = sqlalchemy.Column(sqlalchemy.String)

class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    products = orm.relation('Product')

    


name = config.DATABASE
global_init(name)
session = create_session()


def add_new_product(product):
    #create new product from dictionary values
    print("Category name", product["category_id"])
    category = get_category(product["category_id"])
    if not category:
        category = add_category(product["category_id"])
        print("New category", category.id, category.name)

    product["category_id"] = category.id
    print("category", category.id, category.name)
    dbProduct = Product(**product)
    
    session.add(dbProduct)
    session.commit()
    return dbProduct.id

def get_category(name):
    try:
        return session.query(Category).filter(Category.name==name).one()
    except:
        return None
    
def get_category_by_id(id):
    try:
        return session.query(Category).get(id)
    except:
        return None


def add_category(name):
    newCaterogy = Category(name=name)
    session.add(newCaterogy)
    session.flush()
    print("New category", newCaterogy.id, newCaterogy.name)
    return newCaterogy

def update_product(id, **args):
    product = get_product(id)
    for key in args:
        if hasattr(product, key):
            setattr(product, key, args[key])
    session.commit()
    return

def get_product(id) -> Product:
    return session.query(Product).get(id)

def to_readable(product):
    productDict = {}
    productDict["name"] = product.name
    productDict["stars"] = "?"
    if product.stars:
        productDict["stars"] = int(product.stars)
    productDict["description"] = product.description
    
    category = get_category_by_id(product.category_id)
    if category:
        productDict["category"] = category.name

    productDict["photo"] = product.photo
    return productDict


def get_product_readable(id):
    product = get_product(id)
    if product:
        return to_readable(product)
    return None

def get_categories():
    return session.query(Category)

def search_by_category(category):
    catID = get_category(category).id
    return session.query(Product).filter(Product.category_id==catID).all()
    
def search_by_name(name):
    try:
        return session.query(Product).filter(Product.name==name).first()
    except:
        return None

def search_by_review(minStars):
    return session.query(Product).filter(Product.stars>=minStars)

def get_products():
    return session.query(Product)
