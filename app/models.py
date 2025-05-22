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
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    gender = db.Column(db.String(10), nullable=False, default='Laki-laki')
    religion = db.Column(db.String(20), nullable=False, default='Islam')
    major = db.Column(db.String(50), nullable=True)
    form_data = db.Column(db.Text, nullable=False, default='{}')
    full_name = db.Column(db.String(100))
    birth_place = db.Column(db.String(100))
    birth_date = db.Column(db.String(20))  # Changed to String for date storage
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    previous_school = db.Column(db.String(100))
    initial_form_submitted = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # Add payment status
    
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

    def validate_field_value(self, value):
        """Validate if a field value is actually filled with meaningful data"""
        if value is None:
            return False
        if isinstance(value, str):
            # Remove whitespace and check if empty
            cleaned = value.strip()
            # Check for common placeholder values
            invalid_values = ['Pilih', 'Select', '-', 'None', 'Tidak Ada']
            return cleaned and not any(invalid in cleaned for invalid in invalid_values)
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, bool):
            return value
        if isinstance(value, (bytes, bytearray)):
            return len(value) > 0
        if isinstance(value, (list, dict, set)):
            return bool(value)
        return bool(value)

    def calculate_profile_completion(self):
        """Calculate profile completion percentage with strict validation"""
        required_fields = {
            'full_name': (self.full_name, 15),           # Basic identity
            'birth_place': (self.birth_place, 10),
            'birth_date': (self.birth_date, 10),
            'gender': (self.gender, 10),
            'religion': (self.religion, 5),
            
            'phone': (self.phone, 10),                   # Contact info  
            'address': (self.address, 15),
            
            'parent_name': (self.parent_name, 10),       # Parent info
            'parent_phone': (self.parent_phone, 5),
            
            'previous_school': (self.previous_school, 5), # Education
            'major': (self.major, 5)                     # Program selection
        }
        
        total_weight = sum(weight for _, weight in required_fields.items())
        completed_weight = sum(weight for (value, weight) in required_fields.items() 
                             if self.validate_field_value(value))
        
        return int((completed_weight / total_weight * 100) if total_weight > 0 else 0)
        def validate_document(self, data):
            """Check if document data is valid"""
            if not data:
                return False
            # Ensure document has actual content (at least 1KB)
            min_size = 1024  # 1KB
            if isinstance(data, (bytes, bytearray)) and len(data) < min_size:
                return False
            return True

    def calculate_document_completion(self):
        """Calculate document completion percentage with strict validation"""
        # Required documents with weights
        required_docs = {
            'graduation_certificate_data': (self.graduation_certificate_data, 25), # Most important
            'birth_certificate_data': (self.birth_certificate_data, 20),
            'family_card_data': (self.family_card_data, 20),
            'photo_data': (self.photo_data, 20),
            'report_card_data': (self.report_card_data, 15)
        }
        
        # Add track-specific document requirement if track is selected
        if self.registration_track:
            track_docs = {
                'achievement': (self.achievement_docs_data, 30),
                'affirmation': (self.affirmation_docs_data, 30), 
                'domicile': (self.domicile_docs_data, 30)
            }
            if self.registration_track in track_docs:
                required_docs['track_document'] = track_docs[self.registration_track]
        
        total_weight = sum(weight for _, weight in required_docs.values())
        completed_weight = sum(weight for (data, weight) in required_docs.values() 
                             if self.validate_document(data))
        
        return int((completed_weight / total_weight * 100) if total_weight > 0 else 0)

    @property
    def progress_percentage(self):
        """Calculate overall progress with weighted components and validation"""
        # Get base completion percentages
        profile_completion = self.calculate_profile_completion()
        document_completion = self.calculate_document_completion()
        
        # If nothing is filled out, return 0
        if profile_completion == 0 and document_completion == 0:
            return 0
            
        # Weight components
        profile_weight = 0.4   # Profile is 40% of total
        document_weight = 0.6  # Documents are 60% of total
        base_completion = (profile_completion * profile_weight) + (document_completion * document_weight)

        # Ensure base completion reflects actual progress
        if base_completion < profile_completion * profile_weight:
            return int(profile_completion * profile_weight)
        if base_completion < document_completion * document_weight:
            return int(document_completion * document_weight)
        
        # Status and payment adjustments
        if self.status == 'accepted':
            if self.payment_status == 'verified':
                # Only return 100% if everything is complete
                if profile_completion > 90 and document_completion > 90:
                    return 100
                # High completion but not perfect
                return 95 if base_completion > 90 else 90
            # Accepted but payment pending
            return min(85, base_completion + 10)
            
        elif self.status == 'rejected':
            # Cap rejected applications
            return min(85, base_completion)
        
        # Payment status adjustments for pending applications
        if self.payment_status == 'verified':
            if profile_completion > 90 and document_completion > 90:
                return min(95, base_completion + 10)
            return min(90, base_completion + 5)
        elif self.payment_status == 'submitted':
            return min(85, base_completion + 5)
        
        # Regular progress
        if base_completion > 0:
            # Ensure minimum progress reflects actual work
            return max(min(base_completion, 80), 
                      min(10, profile_completion + document_completion))
        
        return 0

    def calculate_document_completion(self):
        """Calculate document completion percentage with weighted documents"""
        required_docs = {
            'graduation_certificate_data': (self.graduation_certificate_data, 25),  # Most important
            'birth_certificate_data': (self.birth_certificate_data, 20),
            'family_card_data': (self.family_card_data, 20),
            'photo_data': (self.photo_data, 20),
            'report_card_data': (self.report_card_data, 15)
        }
        
        # Add track-specific document requirement
        track_docs = {
            'achievement': (self.achievement_docs_data, 30),
            'affirmation': (self.affirmation_docs_data, 30),
            'domicile': (self.domicile_docs_data, 30)
        }
        
        if self.registration_track in track_docs:
            required_docs['track_document'] = track_docs[self.registration_track]
            
        total_weight = sum(weight for _, weight in required_docs.values())
        completed_weight = sum(weight for (data, weight) in required_docs.values() 
                             if data and len(data or b'') > 0)
        
        return round((completed_weight / total_weight) * 100) if total_weight > 0 else 0

    @property 
    def completion_status(self):
        """Returns tuple of (status message, progress class) based on completion"""
        progress = self.progress_percentage
        
        if self.status == 'accepted':
            if self.payment_status == 'verified':
                return ('Pendaftaran Selesai', 'success')
            return ('Diterima - Menunggu Pembayaran', 'info')
            
        elif self.status == 'rejected':
            return ('Pendaftaran Ditolak', 'danger')
            
        elif progress >= 95:
            return ('Menunggu Verifikasi', 'info')
        elif progress >= 75:
            return ('Hampir Selesai', 'primary')
        elif progress >= 50:
            return ('Sedang Diproses', 'warning')
        elif progress >= 25:
            return ('Tahap Awal', 'warning')
        else:
            return ('Belum Lengkap', 'danger')

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

    def check_form_completion(self):
        """Check if all required fields are filled."""
        required_fields = [
            self.full_name,
            self.gender,
            self.birth_place,
            self.birth_date,
            self.address,
            self.phone,
            self.religion,
            self.parent_name,
            self.parent_phone,
            self.previous_school,
            self.major
        ]
        return all(required_fields)

    def update_payment_status(self, status):
        """Update payment status and save to database"""
        self.payment_status = status
        db.session.commit()
        return True

    def update_status(self, status):
        """Update application status and save to database"""
        self.status = status
        if status == 'rejected':
            self.payment_status = 'pending'
        db.session.commit()
        return True

    @property
    def progress_percentage(self):
        """Calculate the completion percentage of the registration form."""
        required_fields = [
            self.full_name,
            self.birth_place,
            self.birth_date,
            self.address,
            self.phone,
            self.parent_name,
            self.parent_phone,
            self.previous_school
        ]
        
        total_fields = len(required_fields)
        filled_fields = sum(1 for field in required_fields if field is not None and field.strip())
        
        # Calculate base percentage from required fields
        base_percentage = (filled_fields / total_fields) * 100
        
        # Round to nearest whole number
        return round(base_percentage)

    def calculate_progress(self):
        """Calculate overall registration progress."""
        progress = 0
        
        # Document progress (50% total - 10% each)
        documents = {
            'graduation_certificate_data': self.graduation_certificate_data,
            'birth_certificate_data': self.birth_certificate_data,
            'family_card_data': self.family_card_data,
            'report_card_data': self.report_card_data,
            'photo_data': self.photo_data
        }
        
        # Add 10% for each uploaded document
        for doc in documents.values():
            if doc is not None:
                progress += 10
        
        # Registration submission progress (20%)
        if self.initial_form_submitted:
            progress += 20
        
        # Document verification progress (20%)
        if self.status == 'verified':
            progress += 20
        
        # Payment completion progress (10%)
        if self.payment_status == 'verified':
            progress += 10
            
        return progress

    def get_progress_class(self):
        """Return the appropriate Bootstrap progress bar class based on progress percentage."""
        progress = self.calculate_progress()
        
        if progress <= 30:
            return 'progress-bar-danger'
        elif progress <= 60:
            return 'progress-bar-warning'
        elif progress <= 90:
            return 'progress-bar-info'
        else:
            return 'progress-bar-success'

    @property
    def progress_percentage(self):
        """Calculate current progress percentage"""
        progress = 0
        
        # Document uploads (50% - 10% each)
        documents = [
            self.graduation_certificate_data,
            self.birth_certificate_data,
            self.family_card_data,
            self.report_card_data,
            self.photo_data
        ]
        progress += sum(10 for doc in documents if doc is not None)
        
        # Registration submission (20%)
        if self.initial_form_submitted:
            progress += 20
        
        # Document verification (20%)
        if self.status == 'accepted':
            progress += 20
        
        # Payment completion (10%)
        if self.payment_status == 'verified':
            progress += 10
            
        return progress

    def get_progress_class(self):
        """Return Bootstrap class based on progress percentage"""
        progress = self.progress_percentage
        
        if progress <= 30:
            return 'progress-bar-danger'
        elif progress <= 60:
            return 'progress-bar-warning'
        elif progress <= 90:
            return 'progress-bar-info'
        else:
            return 'progress-bar-success'