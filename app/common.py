def trueReturn(data, msg):
    return {
        "status": True,
        "data": data,
        "msg": msg
    }


def falseReturn(data, msg):
    return {
        "status": False,
        "data": data,
        "msg": msg
    }

def OrderReturn(data, order, msg):
    return {
        "status" : True,
        "Teas" : data,
        "order" : order,
        "msg" : msg
    }