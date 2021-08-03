import time

from celery import Celery
from celery.bin import celery
from celery.result import AsyncResult
import manage
import ext

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
def sendMsg(recievers,html):
    #注意 在celery的子任务中必须要尝试获取
    with manage.app.test_request_context():
        msg = Message(subject='用户激活-v1.0',
                      recipients=[recievers],
                      sender='mu_tongwu@163.com')
        #需要使用html，如果
        msg.html = html
        ext.mail.send(msg)
        print('邮件发送成功')

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
