from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField





class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    song = FileField('Upload Your Song', validators=[DataRequired(), FileAllowed(['mp3'])])
    submit = SubmitField('Post')




class CommentForm(FlaskForm):
    commnt = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')
    
    
