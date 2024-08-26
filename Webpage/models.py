# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ImageData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(256), nullable=False)
    text_data = db.Column(db.String(256), nullable=False)
    source = db.Column(db.String(50), nullable=False, server_default='upload')
