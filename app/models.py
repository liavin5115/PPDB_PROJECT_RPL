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
    gender = db.Column(db.String(10), nullable=False, default='Laki-laki')  # Add default
    religion = db.Column(db.String(20), nullable=False, default='Islam')  # Add default
    form_data = db.Column(db.Text, nullable=False, default='{}')  # Add default
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
    
    # Track selection and documents
    achievement_docs_data = db.Column(db.LargeBinary)
    achievement_docs_filename = db.Column(db.String(255))
    achievement_docs_mimetype = db.Column(db.String(100))
    affirmation_docs_data = db.Column(db.LargeBinary)
    affirmation_docs_filename = db.Column(db.String(255))
    affirmation_docs_mimetype = db.Column(db.String(100))
    domicile_docs_data = db.Column(db.LargeBinary)
    domicile_docs_filename = db.Column(db.String(255))
    domicile_docs_mimetype = db.Column(db.String(100))
    
    # File metadata 
    file_metadata = db.Column(db.Text, default='{}')  # Add default

    # Document storage fields
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

    # Payment related fields
    payment_status = db.Column(db.String(20), default='unsubmitted')
    payment_proof_data = db.Column(db.LargeBinary)
    payment_proof_filename = db.Column(db.String(255))
    payment_proof_mimetype = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    payment_amount = db.Column(db.Float)
    payment_bank = db.Column(db.String(100))
    payment_account = db.Column(db.String(100))

    @property
    def parsed_form_data(self):
        """Return parsed JSON data"""
        try:
            return json.loads(self.form_data)
        except:
            return {}

    @property
    def parsed_file_metadata(self):
        """Return parsed file metadata as JSON"""
        try:
            return json.loads(self.file_metadata)
        except:
            return {}

    @property
    def progress_status(self):
        """Return current progress status"""
        if self.status == 'rejected':
            return 'rejected'
        elif self.status == 'pending':
            return 'pending'
        elif self.status == 'accepted' and self.payment_status == 'unsubmitted':
            return 'waiting_for_payment'
        elif self.payment_status == 'submitted':
            return 'paid'
        elif self.payment_status == 'verified':
            return 'verified'
        return 'pending'

    @property
    def progress_percentage(self):
        """Return progress percentage"""
        status_weights = {
            'pending': 20,
            'accepted': 40,
            'waiting_for_payment': 60,
            'paid': 80,
            'verified': 100,
            'rejected': 0
        }
        return status_weights.get(self.progress_status, 0)