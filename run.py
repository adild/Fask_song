from flasksong import app

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


'''
from flasksong import db
from flasksong.models import User, Post, Comments_on_post
db.create_all()
user = User.query.first()
User.query.all()
Post.query.all()
Comments_on_post.query.all()
db.drop_all()



'''
