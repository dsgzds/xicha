import json
import datetime
from flask import jsonify, request
from app.users.model import Users, Extras, TeaInOrder, OrderModel, TeaModel, Tags
from app.auth.auths import Auth
from app import db
from resource.order import order_schema
from .. import common


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

    @app.route('/order', methods=['POST', 'GET'])
    def post():
        if request.method == 'POST':
            '''
            data = request.get_json()
            Tea = []
            ordered_list = data['Tea']  # list of dictionaries
    
            for ordered_item in data['Tea']:
                name = ordered_item['name']
                shop = ordered_item['shop']
                price = db.session.query(TeaModel.price).fliter(TeaModel.name == name).all()
                extras = ordered_item['extra'].split('+')
                for extra in extras:
                    price += db.session.query(Extras.price).fliter(Extras.name == extra).all()
                res = TeaModel.find_by_name(name)
                if not res:
                    return {"msg": "Tea not present {}".format(name)}, 404
                Tea.append(TeaInOrder(tea_id=TeaModel.find_id(name)))
            print(Tea)
            # user = json.loads(init_api.get())
            # username = user['name']
            # phonenum = user['phonenum']
            '''
            Tea = request.form.get('name')
            print(Tea)
            Tea_info = TeaModel.query.filter(TeaModel.name == Tea).first()
            Tea_id = Tea_info.id
            price = Tea_info.price
            extras = request.form.get('extras')
            extras = extras.split('+')
            shop = request.form.get('shop')
            time = datetime.datetime.now()
            for extra in extras:
                extra_price = db.session.query(Extras.price).filter(Extras.name == extra).first()
            
                price += extra_price
            order = OrderModel(
                TeaInOrderId=Tea_id,
                status="pending",
                order_time=time,
                # username=username,
                # phonenum=phonenum,
                price=price,
                shop=shop
            )
            order.save_to_db()  # save orders to database

            order.request_with_stripe()  # send the order details to stripe
            print("Payment Done")
            order.change_status("success")

            return order_schema.dump(order)

def GetUserInfo():
    result = Auth.identify(Auth, request)
    if result['status'] and result['data']:
        user = Users.get(Users, result['data'])
        returnUser = {
            'id': user.id,
            'username': user.username,
            'phonenum': user.phonenum
        }
    return returnUser