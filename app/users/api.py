
import datetime
from flask import jsonify, request
from app.users.model import Users, Extras, TeaInOrder, OrderModel, TeaModel, Tags
from app.auth.auths import Auth
from app import db
from schemas.order import OrderSchema
from .. import common
order_schema = OrderSchema()
def init_api(app):
    @app.route('/register', methods=['POST', 'GET'])
    def register():
        """
        用户注册
        :return: json
        """
        if request.method == 'POST':
            phonenum = request.form.get('phonenum')
            username = request.form.get('username')
            password = request.form.get('password')
            user = Users(phonenum=phonenum, username=username, password=Users.set_password(Users, password))
            result = Users.add(Users, user)
            if user.id:
                returnUser = {
                    'id': user.id,
                    'username': user.username,
                    'phonenum': user.phonenum,
                    'login_time': user.login_time
                }
                return jsonify(common.trueReturn(returnUser, "用户注册成功"))
            else:
                return jsonify(common.falseReturn('', '用户注册失败'))

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return jsonify(common.falseReturn('', '用户名和密码不能为空'))
        else:
            return Auth.authenticate(Auth, username, password)

    @app.route('/user', methods=['GET'])
    def get():
        """
        获取用户信息
        :return: json
        """
        result = Auth.identify(Auth, request)
        if result['status'] and result['data']:
            user = Users.get(Users, result['data'])
            returnUser = {
                'id': user.id,
                'username': user.username,
                'phonenum': user.phonenum,
                'login_time': user.login_time
            }
            result = common.trueReturn(returnUser, "请求成功")
        return jsonify(result)

    @app.route('/teainfo_all', methods=['POST', 'GET'])
    def browse_all():
        if request.method == 'POST':
            list = TeaModel.query.filter().all()
            data = TeaModel.to_json(list)

            return jsonify(common.trueReturn(data, "获取全部奶茶信息成功"))

    @app.route('/teainfo_bytag', methods=['POST', 'GET'])
    def browse_bytag():
        if request.method == 'POST':
            tag = request.form.get('tag')
            list = TeaModel.query.filter(TeaModel.tag == tag).all()
            data = TeaModel.to_json(list)

            return jsonify(common.trueReturn(data, "按分类获取奶茶信息成功"))

    @app.route('/teainfo_tags', methods=['POST', 'GET'])
    def browse_tags():
        if request.method == 'POST':
            list = Tags.query.filter().all()
            data = Tags.to_json(list)
            return jsonify(common.trueReturn(data, "获取分类成功"))


    @app.route('/history_order', methods=['POST', 'GET'])
    def HistoryOrder():
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            print(user_id)
            list = OrderModel.query.filter(OrderModel.user_id == user_id).all()
            data = OrderModel.to_json(list)

            return jsonify(common.trueReturn(data, "获取历史订单成功"))

    @app.route('/pay', methods=['POST', 'GET'])
    def pay():
        user_id = request.form.get('user_id')
        user = Users.query.filter(Users.id == user_id).first()
        order_id = request.form.get('order_id')
        order = OrderModel.query.filter(OrderModel.id == order_id).first()
        if user.balance >= order.price:
            user.balance -= order.price
        else:
            return jsonify(common.falseReturn('', "余额不足"))

        user.update()
        order.change_status('payed')
        return jsonify(common.trueReturn('', "支付成功"))

    @app.route('/topup', methods=['POST', 'GET'])
    def topup():
        user_id = request.form.get('user_id')
        user = Users.query.filter(Users.id == user_id).first()
        num = request.form.get('num')
        user.balance += int(num)
        user.update()
        return jsonify(common.trueReturn('', "充值成功"))

    @app.route('/order', methods=['POST', 'GET'])
    def Order():
        if request.method == 'POST':
            data = request.get_json()
            Tea = []
            time = datetime.datetime.now()
            ordered_list = data['Tea']  # list of dictionaries
            price = 0
            user_id = data['user_id']
            for ordered_item in data['Tea']:
                TeaInOrderId = ordered_item['TeaInOrderId']
                shop = ordered_item['shop']

                name = TeaModel.query.filter(TeaModel.id == TeaInOrderId).first().name
                price += sum(db.session.query(TeaModel.price).filter(TeaModel.id == TeaInOrderId).first())
                extras = ordered_item['extras'].split('+')
                for extra in extras:
                    price += sum(db.session.query(Extras.price).filter(Extras.name == extra).first())
                res = TeaModel.find_by_name(name)
                if not res:
                    return {"msg": "Tea not present {}".format(name)}, 404
                Tea.append(TeaInOrder(tea_id=TeaModel.find_id(name)))
            print(Tea)
            # user = json.loads(init_api.get())
            # username = user['name']
            # phonenum = user['phonenum']

            # Tea = request.form.get('name')
            order = OrderModel(
                TeaInOrderId=TeaInOrderId,
                status="pending",
                order_time=time,
                user_id=user_id,
                price=price,
                shop=shop
            )
            order.save_to_db()  # save orders to database
            import time
            # time.sleep(600)
            # order.request_with_stripe()  # send the order details to stripe

            order.change_status("success")

            return order_schema.dump(order)

