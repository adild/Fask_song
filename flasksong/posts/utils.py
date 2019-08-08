import secrets
import os
from flask import current_app

def save_song(form_song):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_song.filename)
    song_fn = random_hex + f_ext
    song_path = os.path.join(current_app.root_path, 'static/user_songs', song_fn)
    form_song.save(song_path)
    return song_fn
