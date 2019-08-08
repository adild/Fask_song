from flask import render_template, request, Blueprint, flash
from flasksong.models import Post, Comments_on_post
from flasksong.posts.forms import CommentForm
from flask_login import current_user
from flasksong import db

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
	page = request.args.get('page', 1, type=int)
	post_id = request.args.get('post_id', type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	comments_model = Comments_on_post.query.order_by(Comments_on_post.date_posted.desc())
	form = CommentForm()
	#likes = Likes_comments.query
	if form.validate_on_submit() and current_user.is_authenticated:
		comments_on_post_obj = Comments_on_post(comments=form.commnt.data, author=current_user, postID=post_id)
		db.session.add(comments_on_post_obj)
		db.session.commit()
		flash('Your comment has been submitted!', 'success')
		
	return render_template('home.html', form=form, posts=posts, comments_model=comments_model)


@main.route("/about")
def about():
    return render_template('about.html', title='About')

