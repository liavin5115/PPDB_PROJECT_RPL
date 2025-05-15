from flask_login import UserMixin
from datetime import datetime
from app import db  # Import db instance from app package
import json

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
        """Parse and return form data as dictionary"""
        try:
            return json.loads(self.form_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    @property
    def parsed_file_metadata(self):
        """Parse and return file metadata as dictionary"""
        try:
            return json.loads(self.file_metadata)
        except (json.JSONDecodeError, TypeError):
            return {}

    @property
    def progress_status(self):
        """Return the current progress status"""
        completion = self.progress_percentage
        if completion == 100:
            return 'complete'
        elif completion > 0:
            return 'in_progress'
        return 'incomplete'

    @property
    def progress_percentage(self):
        """Calculate overall progress percentage"""
        profile_completion = self.calculate_profile_completion()
        document_completion = self.calculate_document_completion()
        return (profile_completion + document_completion) // 2

    @property 
    def completion_status(self):
        """Returns tuple of (status message, progress class) based on completion"""
        profile_completion = self.calculate_profile_completion()
        doc_completion = self.calculate_document_completion()
        
        # Calculate total completion percentage
        total_completion = (profile_completion + doc_completion) / 2
        
        # Define status thresholds and messages
        if total_completion >= 100:
            return ('Complete', 'success')
        elif total_completion >= 75:
            return ('Almost Complete', 'info')
        elif total_completion >= 25:
            return ('In Progress', 'warning') 
        else:
            return ('Just Started', 'danger')

    def calculate_profile_completion(self):
        """Calculate profile completion percentage"""
        required_fields = [
            self.gender,
            self.religion,
            self.form_data  # Assumes form_data contains other required fields
        ]
        
        completed = sum(1 for field in required_fields if field and field != '{}')
        total = len(required_fields)
        
        return (completed / total) * 100

    def calculate_document_completion(self):
        """Calculate document completion percentage"""
        required_docs = [
            self.graduation_certificate_data,
            self.birth_certificate_data,
            self.family_card_data,
            self.report_card_data,
            self.photo_data
        ]
        
        # Add track-specific document check
        if self.registration_track == 'achievement':
            required_docs.append(self.achievement_docs_data)
        elif self.registration_track == 'affirmation':
            required_docs.append(self.affirmation_docs_data)
        elif self.registration_track == 'domicile':
            required_docs.append(self.domicile_docs_data)
            
        completed = sum(1 for doc in required_docs if doc is not None)
        total = len(required_docs)
        
        return (completed / total) * 100

    def get_document_status(self):
        """Return status of all required documents"""
        doc_status = {
            'graduation_certificate': bool(self.graduation_certificate_data),
            'birth_certificate': bool(self.birth_certificate_data),
            'family_card': bool(self.family_card_data),
            'report_card': bool(self.report_card_data),
            'photo': bool(self.photo_data)
        }
        
        # Add track-specific document status
        if self.registration_track:
            track_docs = {
                'achievement': bool(self.achievement_docs_data),
                'affirmation': bool(self.affirmation_docs_data),
                'domicile': bool(self.domicile_docs_data)
            }
            doc_status['track_document'] = track_docs.get(self.registration_track, False)
            
        return doc_status

    def update_field(self, field_name, value):
        """Update a single field and recalculate completion"""
        form_data = self.parsed_form_data
        form_data[field_name] = value
        self.form_data = json.dumps(form_data)
        return self.calculate_profile_completion()

    def update_document(self, document_type, file_data, filename, mimetype):
        """Update document data and return completion percentage"""
        # Map document types to model attributes
        document_map = {
            'graduation_certificate': ('graduation_certificate_data', 'graduation_certificate_filename', 'graduation_certificate_mimetype'),
            'birth_certificate': ('birth_certificate_data', 'birth_certificate_filename', 'birth_certificate_mimetype'),
            'family_card': ('family_card_data', 'family_card_filename', 'family_card_mimetype'),
            'report_card': ('report_card_data', 'report_card_filename', 'report_card_mimetype'),
            'photo': ('photo_data', 'photo_filename', 'photo_mimetype')
        }
        
        if document_type not in document_map:
            raise ValueError('Invalid document type')
            
        # Get the attribute names for this document type
        data_attr, filename_attr, mimetype_attr = document_map[document_type]
        
        # Update the document attributes
        setattr(self, data_attr, file_data)
        setattr(self, filename_attr, filename)
        setattr(self, mimetype_attr, mimetype)
        
        # Calculate and return new completion percentage
        return self.calculate_completion_status()

    def update_personal_info(self, data):
        """Update personal information and form data"""
        # Update direct fields
        if 'gender' in data:
            self.gender = data['gender']
        if 'religion' in data:
            self.religion = data['religion']
            
        # Update form_data
        form_data = self.parsed_form_data
        updateable_fields = [
            'birth_date', 'address', 'phone', 'previous_school'
        ]
        
        for field in updateable_fields:
            if field in data:
                form_data[field] = data[field]
                
        self.form_data = json.dumps(form_data)
        return self.calculate_profile_completion()

    def calculate_completion_status(self):
        """Calculate document completion status"""
        total_required = 5  # Basic required documents
        completed = 0
        
        # Check basic documents
        if self.graduation_certificate_data:
            completed += 1
        if self.birth_certificate_data:
            completed += 1
        if self.family_card_data:
            completed += 1
        if self.report_card_data:
            completed += 1
        if self.photo_data:
            completed += 1
            
        # Calculate percentage
        percentage = (completed / total_required) * 100
        return round(percentage)