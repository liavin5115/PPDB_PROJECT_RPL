import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
from io import BytesIO
import json
from datetime import datetime
from app.models import db, Form, User

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        final_filename = timestamp + filename
        folder_path = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, final_filename)
        file.save(file_path)
        return os.path.join(subfolder, final_filename)
    return None

class AdmissionForm(FlaskForm):
    # Basic fields
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    previous_school = StringField('Previous School', validators=[DataRequired()])
    
    # Required documents
    graduation_certificate = FileField('Graduation Certificate', 
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    birth_certificate = FileField('Birth Certificate',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    family_card = FileField('Family Card',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    report_card = FileField('Report Card',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    photo = FileField('Photo',
        validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    
    # Registration track fields
    registration_track = SelectField('Registration Track',
        choices=[
            ('', 'Select Track'),
            ('achievement', 'Achievement Path'),
            ('affirmation', 'Affirmation Path'),
            ('domicile', 'Domicile Path')
        ], validators=[DataRequired()])
        
    # Track-specific documents with Optional validator
    achievement_docs = FileField('Achievement Documents',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    affirmation_docs = FileField('Affirmation Documents',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    domicile_docs = FileField('Domicile Documents',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])

class PaymentForm(FlaskForm):
    payment_proof = FileField('Payment Proof',
        validators=[FileRequired(), FileAllowed(['jpg', 'png', 'pdf'], 'Images or PDF only!')])

@main.route('/')
def index():
    return render_template('landing_page.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        # Admin dashboard
        forms = Form.query.all()
        return render_template('dashboard_admin.html', forms=forms)
    else:
        # User dashboard
        user_form = Form.query.filter_by(user_id=current_user.id).first()
        admission_form = AdmissionForm()  # Create form instance for new submissions
        payment_form = PaymentForm()  # Create payment form instance
        
        return render_template(
            'dashboard_user.html',
            form=user_form,  # Database record
            admission_form=admission_form,  # Form for submission
            payment_form=payment_form,  # Payment form
            form_status=user_form.status if user_form else None
        )

@main.route('/submit-form', methods=['POST'])
@login_required
def submit_form():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = AdmissionForm()
    if form.validate_on_submit():
        try:
            # Check for existing submission
            if Form.query.filter_by(user_id=current_user.id).first():
                flash('You have already submitted an application.', 'warning')
                return redirect(url_for('main.dashboard'))
            
            # Create form data dictionary
            form_data = {
                'birth_date': form.birth_date.data.strftime('%Y-%m-%d'),
                'address': form.address.data,
                'phone': form.phone.data,
                'previous_school': form.previous_school.data,
                'registration_track': form.registration_track.data
            }
            
            # Handle required documents
            files_data = {}
            for field in ['graduation_certificate', 'birth_certificate', 'family_card', 'report_card', 'photo']:
                file = getattr(form, field).data
                if file:
                    files_data[f'{field}_data'] = file.read()
                    files_data[f'{field}_filename'] = secure_filename(file.filename)
                    files_data[f'{field}_mimetype'] = file.mimetype
            
            # Handle track-specific documents
            track_field_map = {
                'achievement': 'achievement_docs',
                'affirmation': 'affirmation_docs',
                'domicile': 'domicile_docs'
            }
            
            track_field = track_field_map.get(form.registration_track.data)
            if track_field and getattr(form, track_field).data:
                track_file = getattr(form, track_field).data
                files_data['track_document_data'] = track_file.read()
                files_data['track_document_filename'] = secure_filename(track_file.filename)
                files_data['track_document_mimetype'] = track_file.mimetype
            
            # Create new form entry
            new_form = Form(
                user_id=current_user.id,
                form_data=json.dumps(form_data),
                registration_track=form.registration_track.data,
                **files_data
            )
            
            db.session.add(new_form)
            db.session.commit()
            
            flash('Your application has been submitted successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your application.', 'danger')
            print(f"Error: {str(e)}")
            
    return render_template('dashboard_user.html', 
                         form=None, 
                         admission_form=form)

@main.route('/submit-payment', methods=['POST'])
@login_required
def submit_payment():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = PaymentForm()
    if form.validate_on_submit():
        user_form = Form.query.filter_by(user_id=current_user.id).first()
        
        if not user_form or user_form.status != 'accepted':
            flash('Cannot submit payment at this time.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        if form.payment_proof.data:
            file = form.payment_proof.data
            user_form.payment_proof_data = file.read()
            user_form.payment_proof_filename = secure_filename(file.filename)
            user_form.payment_proof_mimetype = file.mimetype
            user_form.payment_status = 'submitted'
            user_form.payment_date = datetime.utcnow()
            
            db.session.commit()
            flash('Payment proof submitted successfully! Waiting for verification.', 'success')
        
        return redirect(url_for('main.dashboard'))
    
    flash('Error submitting payment proof.', 'danger')
    return redirect(url_for('main.dashboard'))

@main.route('/update-status/<int:form_id>', methods=['POST'])
@login_required
def update_status(form_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = Form.query.get_or_404(form_id)
    new_status = request.form.get('status')
    
    if new_status in ['accepted', 'rejected']:
        form.status = new_status
        db.session.commit()
        flash(f'Application status updated to {new_status}', 'success')
    
    return redirect(url_for('main.dashboard'))

@main.route('/verify-payment/<int:form_id>', methods=['POST'])
@login_required
def verify_payment(form_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = Form.query.get_or_404(form_id)
    if form.payment_status == 'submitted':
        form.payment_status = 'verified'
        db.session.commit()
        flash('Payment verified successfully!', 'success')
    
    return redirect(url_for('main.dashboard'))

@main.route('/form-details/<int:form_id>')
@login_required
def form_details(form_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = Form.query.get_or_404(form_id)
    return jsonify({
        'user': form.user.name,
        'form_data': json.loads(form.form_data),
        'status': form.status,
        'timestamp': form.timestamp.strftime('%Y-%m-%d %H:%M')
    })

# Add new route to serve files
@main.route('/download/<int:form_id>/<document_type>')
@login_required
def download_file(form_id, document_type):
    form = Form.query.get_or_404(form_id)
    
    # Security check
    if current_user.role != 'admin' and form.user_id != current_user.id:
        abort(403)
    
    # Map document type to model attributes
    document_map = {
        'graduation_certificate': (form.graduation_certificate_data, 
                                form.graduation_certificate_filename,
                                form.graduation_certificate_mimetype),
        'birth_certificate': (form.birth_certificate_data,
                            form.birth_certificate_filename,
                            form.birth_certificate_mimetype),
        'family_card': (form.family_card_data,
                       form.family_card_filename,
                       form.family_card_mimetype),
        'report_card': (form.report_card_data,
                       form.report_card_filename,
                       form.report_card_mimetype),
        'photo': (form.photo_data,
                 form.photo_filename,
                 form.photo_mimetype),
        'track_document': (form.track_document_data,
                         form.track_document_filename,
                             form.track_document_mimetype),
        # Add track-specific document mappings
        'achievement_docs': (form.achievement_docs_data,
                           form.achievement_docs_filename,
                           form.achievement_docs_mimetype),
        'affirmation_docs': (form.affirmation_docs_data,
                            form.affirmation_docs_filename,
                            form.affirmation_docs_mimetype),
        'domicile_docs': (form.domicile_docs_data,
                         form.domicile_docs_filename,
                         form.domicile_docs_mimetype)
    }
    
    if document_type not in document_map:
        abort(404)
    
    file_data, filename, mimetype = document_map[document_type]
    
    if not file_data:
        abort(404)
    
    return send_file(
        BytesIO(file_data),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

@main.route('/view/<int:form_id>/<document_type>')
@login_required
def view_file(form_id, document_type):
    form = Form.query.get_or_404(form_id)
    
    # Security check
    if current_user.role != 'admin' and form.user_id != current_user.id:
        abort(403)
    
    # Map document type to model attributes
    document_map = {
        'graduation_certificate': (form.graduation_certificate_data, 
                                form.graduation_certificate_filename,
                                form.graduation_certificate_mimetype),
        'birth_certificate': (form.birth_certificate_data,
                            form.birth_certificate_filename,
                            form.birth_certificate_mimetype),
        'family_card': (form.family_card_data,
                       form.family_card_filename,
                       form.family_card_mimetype),
        'report_card': (form.report_card_data,
                       form.report_card_filename,
                       form.report_card_mimetype),
        'photo': (form.photo_data,
                 form.photo_filename,
                 form.photo_mimetype),
        'payment_proof': (form.payment_proof_data,
                         form.payment_proof_filename,
                         form.payment_proof_mimetype),
        'achievement_docs': (form.achievement_docs_data,
                           form.achievement_docs_filename,
                           form.achievement_docs_mimetype),
        'affirmation_docs': (form.affirmation_docs_data,
                            form.affirmation_docs_filename,
                            form.affirmation_docs_mimetype),
        'domicile_docs': (form.domicile_docs_data,
                         form.domicile_docs_filename,
                         form.domicile_docs_mimetype)
    }
    
    if document_type not in document_map:
        abort(404)
    
    file_data, filename, mimetype = document_map[document_type]
    
    if not file_data:
        abort(404)
    
    return send_file(
        BytesIO(file_data),
        mimetype=mimetype,
        as_attachment=False
    )
