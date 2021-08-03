from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
# from Models.order import OrderModel
from app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phonenum = db.Column(db.String(250),  unique=True, nullable=False)
    username = db.Column(db.String(250),  unique=True, nullable=False)
    password = db.Column(db.String(250))
    balance = db.Column(db.Integer)
    login_time = db.Column(db.Integer)
    order_id = db.relationship("OrderModel", backref="user_info")  # 用户下的订单

    def __init__(self, username, password, phonenum):
        self.username = username
        self.password = password
        self.phonenum = phonenum
        self.balance = 100

    def __str__(self):
        return "Users(id='%s')" % self.id

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, hash, password):
        return check_password_hash(hash, password)

    def get(self, id):
        return self.query.filter_by(id=id).first()

    def add(self, user):
        db.session.add(user)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, id):
        self.query.filter_by(id=id).delete()
        return session_commit()


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason


from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


CURRENCY="INR"

class BaseModel:
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间

class TeaInOrder(db.Model):
    __tablename__ = "tea_in_order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tea_id = db.Column("tea_id", db.Integer, db.ForeignKey("tea.id"), nullable=True)
    order_id = db.Column("order_id", db.String(100), db.ForeignKey("orders.id"), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    state = db.Column(db.String(100), nullable=False)
    ice = db.Column(db.String(100), nullable=False)
    sweetness = db.Column(db.String(100), nullable=False)
    lemon = db.Column(db.String(100), nullable=False)
    tea_dreg = db.Column(db.String(100), nullable=False)  # 茶底
    makeway = db.Column(db.String(100), nullable=False)  # 做法
    taste = db.Column(db.String(100), nullable=False)  # 口味
    # order = db.relationship("OrderModel", back_populates="tea")

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

        # 配合todict一起使用

    def to_json(all_vendors):
        v = [ven.dobule_to_dict() for ven in all_vendors]
        return v


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String(15), nullable=False)
    order_time = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    TeaInOrderId = db.Column(db.Integer, db.ForeignKey('tea.id'), nullable=True)
    # TeaInOrder = db.relationship("TeaInOrder", back_populates="order_id", foreign_keys=[TeaInOrderId])
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    shop = db.Column(db.String(100), nullable=True)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @property
    def description(self):
        counts = [f'{data.quantity}x {data.item.name}' for data in self.items]
        return ",".join(counts)

    @property
    def amount(self):
        total = int(sum([item_data.item.price * item_data.quantity for item_data in self.items]) * 100)
        return total

    def change_status(self, new_status):
        self.status = new_status
        self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def status(self):
        tmp_status = self.status
        if self.status == 1:
            tmp_status = self.express_status
            if self.express_status == 1 and self.comment_status == 0:
                tmp_status = -5
            if self.express_status == 1 and self.comment_status == 1:
                tmp_status = 1
        return tmp_status

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    # 配合todict一起使用
    def to_json(all_vendors):
        v = [ven.dobule_to_dict() for ven in all_vendors]
        return v

    '''
    def request_with_stripe(self) -> stripe.Charge:
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 9,
                "exp_year": 2021,
                "cvc": "314",
            }, )

        print("The token id is ", token["id"])
        print("The amount is ", self.amount)

        return stripe.Charge.create(
            amount=self.amount,
            currency=CURRENCY,
            description=self.description,
            source=token["id"],
            shipping={
                'name': "John",
                'address': {
                    'line1': '510 Townsend St',
                    'postal_code': '98140',
                    'city': 'Kolkata',
                    'state': 'WB',
                    'country': 'India',
                }
            })
    '''

from app import db
from typing import Dict, List, Union
from flask_sqlalchemy import SQLAlchemy

ItemJson = Dict[str, Union[int, str, float]]


class TeaModel(db.Model):
    __tablename__ = "tea"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),  nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.String(50), nullable=True)
    images = db.Column(db.String(100), nullable=False)
    db.ForeignKey('Tags.name')



    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    # store = db.relationship("StoreModel")

    def __init__(self, name, tag, price, description, remarks):
        self.name = name
        self.tag = tag
        self.price = price
        self.description = description
        self.remarks = remarks

    @classmethod
    def find_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls) -> List:
        return cls.query.all()

    @classmethod
    def find_id(cls, name: str):
        obj = cls.query.filter_by(name=name).first()
        return obj.id

    @classmethod
    def get_info(cls, name: str):
        info = cls.query.fliter(name == name).first()
        return info

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    # 配合todict一起使用
    def to_json(all_vendors):
        v = [ven.dobule_to_dict() for ven in all_vendors]
        return v

class Tags(db.Model):
    __tablename__ = "Tags"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),  nullable=False)
    db.relationship("TeaModel", backref='subcat')

    def __init__(self, name):
        self.name = name

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    # 配合todict一起使用
    def to_json(all_vendors):
        v = [ven.dobule_to_dict() for ven in all_vendors]
        return v

class Extras(db.Model):
    __tablename__ = "Extras"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50),  nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    # 配合todict一起使用
    def to_json(all_vendors):
        v = [ven.dobule_to_dict() for ven in all_vendors]
        return v



