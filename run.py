from flasksong import app

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)








'''
run SQLAlchemy commands from terminal-->
from flasksong import db
from flasksong.models import User, Post
db.create_all()
user = User.query.first()
db.drop_all()

mysql://sql12300189:ZUdKn7maRm@sql12.freemysqlhosting.net/sql12300189

'''
