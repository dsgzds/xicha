from run import app
from . import api
from utils.response_code import RET
from flask import current_app, jsonify, make_response, send_file
from flask import current_app, jsonify, make_response, send_file, request
from captcha.image import ImageCaptcha
import random
from app.users.model import Users

# 短信验证码的redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔, 单位：秒
SEND_SMS_CODE_INTERVAL = 60

@app.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    code = request.args.get("code")
    code_id = request.args.get("code_id")

    # 校验参数
    if not all([code_id, code]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag:
            # 表示在60秒内之前有过发送的记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60秒后重试")

    # 判断手机号是否存在
    try:
        user = Users.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user:
            # 表示手机号已存在
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 如果手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次出发发送短信的操作
        redis_store.setex("send_sms_code_%s" % mobile, SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

    # 发送短信
    try:
        print('send message')
        result = 0
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")