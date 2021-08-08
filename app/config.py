DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_DB = 'user_info'
DB_PORT = 3306

DEBUG = True
PORT = 3333
HOST = "192.168.178.1"
SECRET_KEY = "abcdefg"
# HOST = "0.0.0.0"

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=DB_USER,password=DB_PASSWORD, host=DB_HOST,port=DB_PORT, db=DB_DB)

# CELERY_BROKER_URL =