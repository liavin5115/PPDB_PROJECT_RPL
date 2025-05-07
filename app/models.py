from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default='user')
    forms = db.relationship('Form', backref='user', lazy=True)

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    form_data = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Document fields
    graduation_certificate = db.Column(db.String(255))
    birth_certificate = db.Column(db.String(255))
    family_card = db.Column(db.String(255))
    report_card = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    
    # Registration track
    registration_track = db.Column(db.String(20))
    track_document = db.Column(db.String(255))
    
    # File metadata
    file_metadata = db.Column(db.Text)  # Store original filenames and upload times

    # Document storage fields (binary data)
    graduation_certificate_data = db.Column(db.LargeBinary)
    graduation_certificate_filename = db.Column(db.String(255))
    graduation_certificate_mimetype = db.Column(db.String(100))
    
    birth_certificate_data = db.Column(db.LargeBinary)
    birth_certificate_filename = db.Column(db.String(255))
    birth_certificate_mimetype = db.Column(db.String(100))
    
    family_card_data = db.Column(db.LargeBinary)
    family_card_filename = db.Column(db.String(255))
    family_card_mimetype = db.Column(db.String(100))
    
    report_card_data = db.Column(db.LargeBinary)
    report_card_filename = db.Column(db.String(255))
    report_card_mimetype = db.Column(db.String(100))
    
    photo_data = db.Column(db.LargeBinary)
    photo_filename = db.Column(db.String(255))
    photo_mimetype = db.Column(db.String(100))
    
    track_document_data = db.Column(db.LargeBinary)
    track_document_filename = db.Column(db.String(255))
    track_document_mimetype = db.Column(db.String(100))

    @property
    def parsed_form_data(self):
        """Return parsed JSON data"""
        try:
            if isinstance(self.form_data, str):
                return json.loads(self.form_data)
            return self.form_data
        except:
            return {}

    @property
    def parsed_file_metadata(self):
        """Return parsed file metadata as JSON"""
        try:
            return json.loads(self.file_metadata) if self.file_metadata else {}
        except:
            return {}