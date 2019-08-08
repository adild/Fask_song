from flask import render_template, url_for, flash, request, redirect, abort, Blueprint
from flask_login import current_user, login_required
from flasksong import db
from flasksong.models import Post
from flasksong.posts.forms import PostForm
from flasksong.posts.utils import save_song


posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.song.data:
            song_file_temp = save_song(form.song.data)
            #current_user.song_file = song_file
        post = Post(title=form.title.data, song_file=song_file_temp, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Update Post')

@posts.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		if form.song.data:
			song_file_temp = save_song(form.song.data)
		post.title = form.title.data
		post.song_file = song_file_temp
		db.session.commit()
		flash('Your post has been Updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
	return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')



@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))



@posts.route("/likes_incr/<int:post_id>")
@login_required
def likes_incr(post_id):
	post = Post.query.get_or_404(post_id)
	post.likes = post.likes + 1
	db.session.commit()
	#flash('You like it', 'success')
	return redirect(request.referrer)


