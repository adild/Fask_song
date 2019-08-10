from flasksong import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments_on_post_user = db.relationship('Comments_on_post', backref='author', lazy=True)
    followers_following = db.relationship('Followers_following', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
    	s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    	return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
    	s = Serializer(current_app.config['SECRET_KEY'])
    	try:
    		user_id = s.loads(token)['user_id']
    	except:
    		return None
    	return User.query.get(user_id)

    def __repr__(self):
    	return f"User('{self.id}', '{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
	song_file = db.Column(db.String(20), nullable=False)
	likes = db.Column(db.Integer, nullable=False, default=0)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	
	comments_on_post = db.relationship('Comments_on_post', backref='author2', lazy=True)

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"


class Comments_on_post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	comments = db.Column(db.String(200), nullable=True)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	postID = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

	def __repr__(self):
		return f"Comments_on_post('{self.comments}')"


class Followers_following(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	followers = db.Column(db.String(20), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Followers_following('{self.id}', '{self.followers}', '{self.date_posted}', '{self.user_id}')"



