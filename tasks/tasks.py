import time
from flask import jsonify, request
from celery import Celery
from celery.bin import celery
from celery.result import AsyncResult


app = Celery('tasks',
             backend='redis://:123456@10.35.163.24:6379/orders',
             broker='redis://:123456@10.35.163.24:6379/8')  #   :密码@host/post/db

@app.task   #交给Celery队列去调用
def goOrder(order_id):
    print('--goOrder--')
    time.sleep(5)
    print('完成{}的订单'.format(order_id))

    return '{} 确认完成'.format(order_id)

def orderCallback(id,value):

    print(id,'----订单完成----',value)

@app.task
def Make(order_id):
    #注意 在celery的子任务中必须要尝试获取

    p = PayedOrder.objects.filter(start=1).first()
    if p is None:
        return JsonResponse({"msg": "无正在制作的订单"})
    if cal_difftime(p.time_joined, str(datetime.now())) >= 1:
        h = HisOrder(pro=p.pro, conf=p.conf, address=p.address, phonenumber=p.phonenumber, peo=p.peo,
                     user_id=p.user_id, price=p.price)
        next_order = PayedOrder.objects.filter(id=p.id + 1).first()
        if next_order is not None:
            next_order.start = 1
            next_order.time_joined = str(datetime.now())
            next_order.save()
        h.save()
        p.delete()
    return jsonify(common.trueReturn('', "订单完成"))

if __name__ == '__main__':
    print('--批量下订单--')
    for i in range(20):
        #向celery发送任务，并获取异步结果对象
        result:AsyncResult = goOrder.delay('XB99900888'+str(i))
        #实时获取结果（任务执行结果）
        #result.get(timeout=1,interval=0.5,callback=orderCallback)
        print(result.get_leaf())
    print('--下订单已完成--')

if __name__ == '__main1__':
    celery.worker_main()
