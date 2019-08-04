import secrets
import os
from flask import render_template, url_for, flash, request, redirect, abort
from flasksong import app, db, bcrypt, mail 
from flasksong.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, RequestResetForm, ResetPasswordForm
from flasksong.models import User, Post, Comments_on_post
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from flask_mail import Message


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
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


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_song(form_song):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_song.filename)
    song_fn = random_hex + f_ext
    song_path = os.path.join(app.root_path, 'static/user_songs', song_fn)
    form_song.save(song_path)
    return song_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
    
@app.route("/post/new", methods=['GET', 'POST'])
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

@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)



@app.route("/likes_incr/<int:post_id>")
@login_required
def likes_incr(post_id):
	post = Post.query.get_or_404(post_id)
	post.likes = post.likes + 1
	db.session.commit()
	#flash('You like it', 'success')
	return redirect(request.referrer)


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password reset request', sender='noreply@demo.com', recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you didnt make this request then simply ignore this email.
'''
	mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
	    return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
	    user = User.query.filter_by(email=form.email.data).first()
	    send_reset_email(user) 
	    flash('An email has been sent with instructions to reset your password.', 'info')
	    return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
	    return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None: 
	    flash('Invalid or Expired token', 'warning')
	    return redirect(url_for('reset_request'))	
	form = ResetPasswordForm()
	if form.validate_on_submit():
	    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
	    user.password = hashed_password
	    db.session.commit()
	    flash('Your Password has been updated! You are now able to log in', 'success')
	    return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)


'''
@app.route("/comment/<int:post_id>", methods=['GET', 'POST'])
@login_required
def comment(post_id):
	form = CommentForm()
	if form.validate_on_submit():
		comments_on_post_obj = Comments_on_post(comments=form.commnt.data, author=current_user, postID=post_id)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('home.html', form=form)
	
'''	
