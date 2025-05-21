import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from datetime import datetime
import json
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
    
    gender = SelectField('Jenis Kelamin', 
        choices=[
            ('', 'Pilih Jenis Kelamin'),
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan')
        ], validators=[DataRequired()])
    
    religion = SelectField('Agama',
        choices=[
            ('', 'Pilih Agama'),
            ('Islam', 'Islam'),
            ('Kristen', 'Kristen'),
            ('Katolik', 'Katolik'),
            ('Hindu', 'Hindu'),
            ('Buddha', 'Buddha'),
            ('Konghucu', 'Konghucu'),
            ('Lainnya', 'Lainnya')
        ], validators=[DataRequired()])
    
    # Make documents optional by using Optional() validator
    graduation_certificate = FileField('Graduation Certificate', 
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    birth_certificate = FileField('Birth Certificate',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    family_card = FileField('Family Card',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    report_card = FileField('Report Card',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    photo = FileField('Photo',
        validators=[Optional(), FileAllowed(['jpg', 'png'])])
    
    # Registration track fields remain optional
    registration_track = SelectField('Registration Track',
        choices=[
            ('', 'Select Track'),
            ('achievement', 'Achievement Path'),
            ('affirmation', 'Affirmation Path'),
            ('domicile', 'Domicile Path')
        ], validators=[Optional()])
        
    # Track-specific documents remain optional
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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing_page.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # For admin users
    if current_user.role == 'admin':
        forms = Form.query.all()
        
        # Authentication check
        if not forms:
            forms = []
            
        # Calculate application statistics
        status_stats = {
            'total': len(forms),
            'pending': len([f for f in forms if f.status == 'pending']),
            'accepted': len([f for f in forms if f.status == 'accepted']),
            'rejected': len([f for f in forms if f.status == 'rejected'])
        }
        
        # Calculate payment statistics
        payment_stats = {
            'verified': len([f for f in forms if f.payment_status == 'verified']),
            'pending': len([f for f in forms if f.payment_status == 'pending']),
            'unsubmitted': len([f for f in forms if f.payment_status == 'unsubmitted'])
        }
        
        # Calculate gender distribution
        gender_stats = {
            'Laki-laki': len([f for f in forms if f.gender == 'Laki-laki']),
            'Perempuan': len([f for f in forms if f.gender == 'Perempuan'])
        }
        
        # Calculate track distribution
        track_stats = {
            'achievement': len([f for f in forms if f.registration_track == 'achievement']),
            'affirmation': len([f for f in forms if f.registration_track == 'affirmation']),
            'domicile': len([f for f in forms if f.registration_track == 'domicile'])
        }
        
        # Get recent forms
        recent_forms = sorted(forms, key=lambda x: x.timestamp, reverse=True)[:5]
        
        return render_template(
            'dashboard_admin.html',
            forms=forms,
            status_stats=status_stats,
            payment_stats=payment_stats,
            gender_stats=gender_stats,
            track_stats=track_stats,
            recent_forms=recent_forms,
            datetime=datetime
        )
        
    # For regular users
    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        form = Form(user_id=current_user.id)
        db.session.add(form)
        db.session.commit()
        
    # Create forms as needed
    admission_form = None if form else AdmissionForm()
    payment_form = PaymentForm() if form and form.status == 'accepted' and form.payment_status != 'verified' else None
    
    return render_template(
        'dashboard_user.html',
        form=form,
        admission_form=admission_form,
        payment_form=payment_form
    )

def get_status_message(status):
    messages = {
        'complete': 'Your profile is complete! All documents have been uploaded.',
        'in_progress': 'Keep going! Complete your profile and upload remaining documents.',
        'incomplete': 'Please complete your profile and upload required documents.'
    }
    return messages.get(status, 'Please complete your registration.')

@main.route('/submit-form', methods=['POST'])
@login_required
def submit_form():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
    
    form = AdmissionForm()
    if form.validate_on_submit():
        try:
            # Create new form or get existing
            user_form = Form.query.filter_by(user_id=current_user.id).first()
            if not user_form:
                user_form = Form(user_id=current_user.id)
                db.session.add(user_form)
            
            # Update basic info
            form_data = {
                'birth_date': form.birth_date.data.strftime('%Y-%m-%d'),
                'address': form.address.data,
                'phone': form.phone.data,
                'previous_school': form.previous_school.data
            }
            
            user_form.gender = form.gender.data
            user_form.religion = form.religion.data
            user_form.form_data = json.dumps(form_data)
            
            # Handle optional document uploads
            documents = {
                'graduation_certificate': form.graduation_certificate,
                'birth_certificate': form.birth_certificate,
                'family_card': form.family_card,
                'report_card': form.report_card,
                'photo': form.photo
            }
            
            for doc_name, doc_field in documents.items():
                if doc_field.data:
                    file = doc_field.data
                    setattr(user_form, f'{doc_name}_data', file.read())
                    setattr(user_form, f'{doc_name}_filename', secure_filename(file.filename))
                    setattr(user_form, f'{doc_name}_mimetype', file.mimetype)
            
            # Handle optional track selection and documents
            if form.registration_track.data:
                user_form.registration_track = form.registration_track.data
                track_docs = {
                    'achievement': form.achievement_docs,
                    'affirmation': form.affirmation_docs,
                    'domicile': form.domicile_docs
                }
                if form.registration_track.data in track_docs:
                    track_doc = track_docs[form.registration_track.data]
                    if track_doc.data:
                        user_form.track_document_data = track_doc.data.read()
                        user_form.track_document_filename = secure_filename(track_doc.data.filename)
                        user_form.track_document_mimetype = track_doc.data.mimetype
            
            db.session.commit()
            flash('Form submitted successfully! You can upload or update documents later.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error submitting form. Please try again.', 'danger')
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

@main.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if current_user.role == 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        return jsonify({'error': 'No form found'}), 404
        
    data = request.json
    try:
        completion = form.update_personal_info(data)
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'completion': completion
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/update-document/<document_type>', methods=['POST'])
@login_required
def update_document(document_type):
    if current_user.role == 'admin':
        return jsonify({'error': 'Admins cannot submit documents'}), 403
        
    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        return jsonify({'error': 'No form found'}), 404
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    try:
        # Read file data and update document
        file_data = file.read()
        completion = form.update_document(
            document_type,
            file_data,
            secure_filename(file.filename),
            file.content_type
        )
        
        # Commit changes to database
        db.session.commit()
        
        return jsonify({
            'message': f'{document_type} updated successfully',
            'completion': completion
        })
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/update-personal-info', methods=['POST'])
@login_required
def update_personal_info():
    if current_user.role == 'admin':
        return jsonify({'success': False, 'message': 'Admin cannot submit forms'}), 403

    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        return jsonify({'success': False, 'message': 'Form not found'}), 404

    try:
        data = request.json
        # Update personal information
        if 'gender' in data:
            form.gender = data['gender']
        if 'religion' in data:
            form.religion = data['religion']
        
        # Update form data fields
        form_data = form.parsed_form_data
        updateable_fields = [
            'birth_date',
            'address', 
            'phone',
            'previous_school'
        ]
        
        for field in updateable_fields:
            if field in data:
                form_data[field] = data[field]
        
        form.form_data = json.dumps(form_data)
        db.session.commit()

        completion = form.calculate_profile_completion()
        return jsonify({
            'success': True,
            'completion': completion,
            'message': 'Personal information updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Error updating information: {str(e)}'
        }), 500

@main.route('/admin/table')
@login_required
def table_view():
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    forms = Form.query.all()
    return render_template('Simple_Table_admin.html', forms=forms)
