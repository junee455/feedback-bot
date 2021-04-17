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
    
    category = orm.relation('Category', back_populates="products")
    category_id = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("categories.id"))



class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    products = orm.relation('Product')

    


name = config.DATABASE
global_init(name)
session = create_session()


def add_new_product(product: Product) -> None:
    session.add(product)
    session.commit()
    return


def update_product(id, **args):
    product = get_product(id)
    for key in args:
        if hasattr(product, key):
            setattr(product, key, args[key])
    session.commit()
    return

def get_product(id) -> Product:
    return session.query(Product).get(id)

def get_products():
    return session.query(Product)
