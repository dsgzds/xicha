# 导入app工程
from run import app
# 导入数据库
from app import db
# 导入Manager用来设置应用程序可通过指令操作
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

# 构建指令，设置当前app受指令控制（即将指令绑定给指定app对象）
manage = Manager(app)
# 构建数据库迁移操作，将数据库迁移指令绑定给指定的app和数据库
migrate = Migrate(app,db)
# 添加数据库迁移指令，该操作保证数据库的迁移可以使用指令操作
manage.add_command('db',MigrateCommand)

#以下为当指令操作runserver时，开启服务。
if __name__ == '__main__':
    manage.run()