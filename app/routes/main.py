import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from io import BytesIO
import json
from datetime import datetime
from app.models import db, Form, User

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

main = Blueprint('main', 'main')

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
    # Existing fields
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    previous_school = StringField('Previous School', validators=[DataRequired()])
    
    # Document uploads
    graduation_certificate = FileField('Graduation Certificate/SKL', 
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'], 'PDF or images only!')])
    birth_certificate = FileField('Birth Certificate',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    family_card = FileField('Family Card (KK)',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    report_card = FileField('Report Card Summary',
        validators=[FileRequired(), FileAllowed(['pdf', 'jpg', 'png'])])
    photo = FileField('Passport Photo',
        validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    
    # Registration track
    registration_track = SelectField('Registration Track',
        choices=[
            ('', 'Select Track'),
            ('achievement', 'Achievement Track'),
            ('affirmation', 'Affirmation Track'),
            ('domicile', 'Domicile Track')
        ],
        validators=[DataRequired()])
    
    track_document = FileField('Track-specific Document',
        validators=[FileAllowed(['pdf', 'jpg', 'png'])])

@main.route('/')
def index():
    return render_template('landing_page.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        forms = Form.query.all()
        return render_template('dashboard_admin.html', forms=forms)
    
    form = AdmissionForm()
    user_form = Form.query.filter_by(user_id=current_user.id).first()
    form_status = user_form.status if user_form else None
    form_submitted = bool(user_form)
    
    return render_template('dashboard_user.html', 
                         form=form,
                         form_status=form_status,
                         form_submitted=form_submitted)

@main.route('/submit-form', methods=['POST'])
@login_required
def submit_form():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = AdmissionForm()
    if form.validate_on_submit():
        if Form.query.filter_by(user_id=current_user.id).first():
            flash('You have already submitted an application.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        # Save basic form data
        form_data = {
            'birth_date': form.birth_date.data.strftime('%Y-%m-%d'),
            'address': form.address.data,
            'phone': form.phone.data,
            'previous_school': form.previous_school.data
        }
        
        # Create new form instance
        new_form = Form(
            user_id=current_user.id,
            form_data=json.dumps(form_data),
            status='pending',
            registration_track=form.registration_track.data
        )
        
        # Store required documents
        if form.graduation_certificate.data:
            file = form.graduation_certificate.data
            new_form.graduation_certificate_data = file.read()
            new_form.graduation_certificate_filename = secure_filename(file.filename)
            new_form.graduation_certificate_mimetype = file.mimetype
            
        if form.birth_certificate.data:
            file = form.birth_certificate.data
            new_form.birth_certificate_data = file.read()
            new_form.birth_certificate_filename = secure_filename(file.filename)
            new_form.birth_certificate_mimetype = file.mimetype
            
        if form.family_card.data:
            file = form.family_card.data
            new_form.family_card_data = file.read()
            new_form.family_card_filename = secure_filename(file.filename)
            new_form.family_card_mimetype = file.mimetype
            
        if form.report_card.data:
            file = form.report_card.data
            new_form.report_card_data = file.read()
            new_form.report_card_filename = secure_filename(file.filename)
            new_form.report_card_mimetype = file.mimetype
            
        if form.photo.data:
            file = form.photo.data
            new_form.photo_data = file.read()
            new_form.photo_filename = secure_filename(file.filename)
            new_form.photo_mimetype = file.mimetype
        
        # Handle track-specific document
        if form.registration_track.data and form.track_document.data:
            file = form.track_document.data
            new_form.track_document_data = file.read()
            new_form.track_document_filename = secure_filename(file.filename)
            new_form.track_document_mimetype = file.mimetype
        
        db.session.add(new_form)
        db.session.commit()
        
        flash('Your application has been submitted successfully!', 'success')
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
                         form.track_document_mimetype)
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
        'track_document': (form.track_document_data,
                         form.track_document_filename,
                         form.track_document_mimetype)
    }
    
    if document_type not in document_map:
        abort(404)
    
    file_data, filename, mimetype = document_map[document_type]
    
    if not file_data:
        abort(404)
    
    return send_file(
        BytesIO(file_data),
        mimetype=mimetype,
        as_attachment=False  # This makes it display in browser instead of downloading
    )