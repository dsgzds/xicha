from app.users.model import OrderModel
from flask_marshmallow import Marshmallow

ma=Marshmallow()
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderModel
        load_only = ("token",)
        dump_only = ("id","status")
        include_fk = True
