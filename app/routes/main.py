import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from datetime import datetime, timedelta
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
    major = SelectField('Program Keahlian', choices=[
        ('', 'Pilih Program Keahlian'),
        ('Teknik Komputer dan Jaringan', 'Teknik Komputer dan Jaringan'),
        ('Rekayasa Perangkat Lunak', 'Rekayasa Perangkat Lunak'),
        ('Multimedia', 'Multimedia')
    ], validators=[DataRequired(message="Pilih program keahlian")])
    
    # Personal Information
    full_name = StringField('Nama Lengkap', validators=[DataRequired()])
    birth_place = StringField('Tempat Lahir', validators=[DataRequired()])
    birth_date = DateField('Tanggal Lahir', validators=[DataRequired()])
    address = TextAreaField('Alamat', validators=[DataRequired()])
    phone = StringField('Nomor Telepon', validators=[DataRequired()])
    previous_school = StringField('Asal Sekolah', validators=[DataRequired()])
    
    # Demographics
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
    
    # Documents
    graduation_certificate = FileField('Ijazah/SKL', 
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    birth_certificate = FileField('Akta Kelahiran',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    family_card = FileField('Kartu Keluarga',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    report_card = FileField('Rapor',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    photo = FileField('Pas Foto',
        validators=[Optional(), FileAllowed(['jpg', 'png'])])
    
    # Registration track
    registration_track = SelectField('Jalur Pendaftaran',
        choices=[
            ('', 'Pilih Jalur Pendaftaran'),
            ('achievement', 'Jalur Prestasi'),
            ('affirmation', 'Jalur Afirmasi'),
            ('domicile', 'Jalur Zonasi')
        ], validators=[DataRequired(message="Pilih jalur pendaftaran")])
    
    # Track-specific documents
    achievement_docs = FileField('Dokumen Prestasi',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    affirmation_docs = FileField('Dokumen Afirmasi',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])
    domicile_docs = FileField('Dokumen Zonasi',
        validators=[Optional(), FileAllowed(['pdf', 'jpg', 'png'])])

class PaymentForm(FlaskForm):
    payment_proof = FileField('Bukti Pembayaran',
        validators=[FileRequired(), FileAllowed(['jpg', 'png', 'pdf'], 'Images or PDF only!')])

@main.route('/')
def index():
    return render_template('landing_page.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Create form instances
    admission_form = AdmissionForm()
    payment_form = PaymentForm()
    
    if current_user.role == 'admin':
        # Get current datetime for template
        current_datetime = datetime.now()
        
        # Get basic statistics
        total_applicants = Form.query.count()
        accepted_count = Form.query.filter_by(status='accepted').count()
        rejected_count = Form.query.filter_by(status='rejected').count()
        pending_count = Form.query.filter_by(status='pending').count()
        payment_verified_count = Form.query.filter_by(payment_status='verified').count()

        # Get registration trend data (last 7 days)
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=6)
        dates = []
        counts = []
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            count = Form.query.filter(
                db.func.date(Form.timestamp) == date
            ).count()
            dates.append(date.strftime('%d/%m'))
            counts.append(count)

        # Calculate daily increase
        yesterday_count = Form.query.filter(
            db.func.date(Form.timestamp) == (today - timedelta(days=1))
        ).count()
        today_count = Form.query.filter(
            db.func.date(Form.timestamp) == today
        ).count()
        daily_increase = today_count - yesterday_count if today_count and yesterday_count else 0

        # Get gender distribution
        male_count = Form.query.filter_by(gender='Laki-laki').count()
        female_count = Form.query.filter_by(gender='Perempuan').count()
        gender_counts = {'male': male_count, 'female': female_count}

        # Get religion distribution
        religions = ['Islam', 'Kristen', 'Katolik', 'Hindu', 'Buddha', 'Konghucu', 'Lainnya']
        religion_counts = []
        for religion in religions:
            count = Form.query.filter_by(religion=religion).count()
            religion_counts.append(count)

        # Get major distribution
        major_codes = ['tkj', 'rpl', 'mm']
        major_names = ['Teknik Komputer dan Jaringan', 'Rekayasa Perangkat Lunak', 'Multimedia']
        major_counts = []
        for code in major_codes:
            count = Form.query.filter_by(major=code).count()
            major_counts.append(count)

        # Get recent registrations
        recent_forms = Form.query.order_by(Form.timestamp.desc()).limit(5).all()        # Get registration trend data (for trend chart)
        # Convert the dates list to JSON-serializable format
        registration_trend_labels = [str(date) for date in dates]
        registration_trend_data = [int(count) for count in counts]

        return render_template('dashboard_admin.html',
                             datetime=datetime,
                             total_applicants=total_applicants,
                             accepted_count=accepted_count,
                             rejected_count=rejected_count,
                             pending_count=pending_count,
                             payment_verified_count=payment_verified_count,
                             daily_increase=daily_increase,
                             registration_dates=dates,
                             registration_counts=counts,
                             gender_counts=gender_counts,
                             religion_counts=religion_counts,
                             major_counts=major_counts,
                             major_names=major_names,
                             recent_forms=recent_forms,
                             registration_trend_labels=registration_trend_labels,
                             registration_trend_data=registration_trend_data)
    else:
        # Get user's current form
        user_form = Form.query.filter_by(user_id=current_user.id).first()
          # Initialize notifications and status details
        notifications = []
        status_details = {
            'current_stage': 0,
            'stages': [
                {
                    'title': 'Pengisian Formulir',
                    'status': 'completed' if user_form and user_form.initial_form_submitted else 'active',
                    'description': 'Mengisi data diri dan dokumen yang diperlukan'
                },
                {
                    'title': 'Verifikasi Dokumen',
                    'status': 'waiting' if not user_form or not user_form.initial_form_submitted else 
                             'completed' if user_form.status == 'accepted' else
                             'active' if user_form.status == 'pending' else 'rejected',
                    'description': 'Pemeriksaan kelengkapan dan keabsahan dokumen'
                },
                {
                    'title': 'Pembayaran Biaya Pendaftaran',
                    'status': 'waiting' if not user_form or user_form.status != 'accepted' else
                             'completed' if user_form.payment_status == 'verified' else
                             'active' if user_form.payment_status == 'submitted' else
                             'pending',
                    'description': 'Melakukan pembayaran dan menunggu verifikasi'
                },
                {
                    'title': 'Pendaftaran Selesai',
                    'status': 'completed' if user_form and user_form.status == 'accepted' and user_form.payment_status == 'verified' else 'waiting',
                    'description': 'Proses pendaftaran telah selesai'
                }
            ]
        }

        if user_form:
            # Set current stage based on status
            if not user_form.initial_form_submitted:
                status_details['current_stage'] = 0
            elif user_form.status == 'pending':
                status_details['current_stage'] = 1
            elif user_form.status == 'accepted' and user_form.payment_status != 'verified':
                status_details['current_stage'] = 2
            elif user_form.status == 'accepted' and user_form.payment_status == 'verified':
                status_details['current_stage'] = 3

            # Add detailed notifications based on status
            if user_form.status == 'pending':
                notifications.append({
                    'type': 'info',
                    'title': 'Dokumen Sedang Diverifikasi',
                    'message': 'Tim kami sedang memeriksa kelengkapan dan keabsahan dokumen Anda. Proses ini biasanya membutuhkan waktu 2-3 hari kerja.'
                })
            elif user_form.status == 'accepted':
                notifications.append({
                    'type': 'success',
                    'title': 'Selamat! Dokumen Anda Diterima',
                    'message': 'Dokumen Anda telah memenuhi syarat. Silakan lanjutkan ke tahap pembayaran biaya pendaftaran.'
                })
                
                # Add detailed payment status notifications
                if not hasattr(user_form, 'payment_status') or user_form.payment_status == 'pending':
                    notifications.append({
                        'type': 'warning',
                        'title': 'Pembayaran Menunggu',
                        'message': 'Silakan melakukan pembayaran biaya pendaftaran sebesar Rp 200.000 melalui rekening yang tertera.'
                    })
                elif user_form.payment_status == 'submitted':
                    notifications.append({
                        'type': 'info',
                        'title': 'Pembayaran Sedang Diverifikasi',
                        'message': 'Bukti pembayaran Anda sedang diverifikasi oleh tim keuangan kami. Proses ini biasanya membutuhkan waktu 1-2 hari kerja.'
                    })
                elif user_form.payment_status == 'verified':
                    notifications.append({
                        'type': 'success',
                        'title': 'Pembayaran Terverifikasi',
                        'message': 'Pembayaran Anda telah diverifikasi'
                    })
        
        return render_template('dashboard_user.html',
                             form=user_form,
                             admission_form=admission_form,
                             payment_form=payment_form,
                             notifications=notifications)

@main.route('/registration-form', methods=['GET', 'POST'])
@login_required
def registration_form():
    # Don't show registration form for admin users
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
        
    # Check if user already has a completed form
    existing_form = Form.query.filter_by(user_id=current_user.id, initial_form_submitted=True).first()
    if existing_form:
        return redirect(url_for('main.dashboard'))
        
    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        form = Form(user_id=current_user.id)
        db.session.add(form)
        db.session.commit()
        
    return render_template('registration_form.html', form=form)

@main.route('/submit-registration', methods=['POST'])
@login_required
def submit_registration():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))
        
    form = Form.query.filter_by(user_id=current_user.id).first()
    if not form:
        form = Form(user_id=current_user.id)
        db.session.add(form)
    
    try:
        # Update form with submitted data
        form.full_name = current_user.name  # Use the user's name from registration
        form.gender = request.form.get('gender')
        form.religion = request.form.get('religion')
        form.birth_place = request.form.get('birth_place')
        form.address = request.form.get('address')
        form.phone = request.form.get('phone')
        form.parent_name = request.form.get('parent_name')
        form.parent_phone = request.form.get('parent_phone')
        form.previous_school = request.form.get('previous_school')

        # Format date to Indonesian format if provided
        birth_date = request.form.get('birth_date')
        if birth_date:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            form.birth_date = birth_date.strftime('%d %B %Y')

        # Set the major if provided
        form.major = request.form.get('major')
        
        # Mark the form as submitted
        form.initial_form_submitted = True
        
        db.session.commit()
        flash('Data pendaftaran berhasil disimpan', 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'danger')
        return redirect(url_for('main.registration_form'))

@main.route('/submit-form', methods=['POST'])
@login_required
def submit_form():
    if current_user.role == 'admin':
        return redirect(url_for('main.dashboard'))

    form_data = request.form
    
    try:
        # Create or update form entry
        form = Form.query.filter_by(user_id=current_user.id).first()
        if not form:
            form = Form(user_id=current_user.id, status='pending')
            db.session.add(form)

        # Update all form fields
        form.full_name = current_user.name
        form.gender = form_data.get('gender')
        form.religion = form_data.get('religion')
        form.birth_place = form_data.get('birth_place')
        form.birth_date = form_data.get('birth_date')
        form.address = form_data.get('address')
        form.phone = form_data.get('phone')
        form.parent_name = form_data.get('parent_name')
        form.parent_phone = form_data.get('parent_phone')  
        form.previous_school = form_data.get('previous_school')
        form.major = form_data.get('major')
        form.initial_form_submitted = True

        db.session.commit()
        flash('Data pendaftaran berhasil disimpan', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'danger')
        print(f"Error saving form: {str(e)}")
    
    return redirect(url_for('main.dashboard'))

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
    if not current_user.role == 'admin':
        flash('Anda tidak memiliki akses untuk melakukan tindakan ini.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    form = Form.query.get_or_404(form_id)
    new_status = request.form.get('status')
    
    if new_status not in ['accepted', 'rejected', 'pending']:
        flash('Status tidak valid.', 'danger')
        return redirect(url_for('main.student_detail', student_id=form_id))
        
    form.update_status(new_status)
    db.session.commit()
    
    status_text = {
        'accepted': 'diterima',
        'rejected': 'ditolak',
        'pending': 'pending'
    }.get(new_status, new_status)
    
    flash(f'Status pendaftaran berhasil diperbarui menjadi {status_text}.', 'success')
    return redirect(url_for('main.student_detail', student_id=form_id))

@main.route('/verify-payment/<int:form_id>', methods=['POST'])
@login_required
def verify_payment(form_id):
    if not current_user.role == 'admin':
        flash('Anda tidak memiliki akses untuk melakukan tindakan ini.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    form = Form.query.get_or_404(form_id)
    
    # Default to 'verified' if no status provided
    payment_status = request.form.get('payment_status', 'verified')
    
    if payment_status not in ['verified', 'rejected']:
        flash('Status pembayaran tidak valid.', 'danger')
        return redirect(url_for('main.student_detail', student_id=form_id))
        
    # Update payment status
    form.payment_status = payment_status
    form.payment_verified_at = datetime.utcnow() if payment_status == 'verified' else None
    db.session.commit()
    
    status_text = 'terverifikasi' if payment_status == 'verified' else 'ditolak'
    flash(f'Pembayaran berhasil {status_text}.', 'success')
    
    return redirect(url_for('main.student_detail', student_id=form_id))

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

@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('main.dashboard'))

    # Get all forms
    forms = Form.query.all()
    
    # Calculate statistics
    total_applicants = len(forms)
    accepted_count = len([f for f in forms if f.status == 'accepted'])
    rejected_count = len([f for f in forms if f.status == 'rejected'])
    pending_count = len([f for f in forms if f.status == 'pending'])
    payment_verified_count = len([f for f in forms if f.status == 'accepted' and 
                                getattr(f, 'payment_status', None) == 'verified'])
    
    # Calculate gender distribution
    gender_counts = {
        'male': len([f for f in forms if f.gender == 'Laki-laki']),
        'female': len([f for f in forms if f.gender == 'Perempuan'])
    }

    # Calculate daily increase (forms submitted in the last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    daily_increase = len([f for f in forms if f.timestamp and f.timestamp > yesterday])

    # Get registration trend data (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_forms = [f for f in forms if f.timestamp and f.timestamp > seven_days_ago]
    
    dates = []
    counts = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        count = len([f for f in recent_forms if f.timestamp.strftime('%Y-%m-%d') == date_str])
        dates.insert(0, date.strftime('%d/%m'))
        counts.insert(0, count)

    # Calculate major distribution
    major_counts = {
        'tkj': len([f for f in forms if f.major == 'tkj']),
        'rpl': len([f for f in forms if f.major == 'rpl']),
        'mm': len([f for f in forms if f.major == 'mm'])
    }

    # Get recent applications (last 5)
    recent_forms = Form.query.order_by(Form.timestamp.desc()).limit(5).all()

    # Define major names for display
    major_names = [
        'Teknik Komputer dan Jaringan',
        'Rekayasa Perangkat Lunak',
        'Multimedia'
    ]

    # Prepare registration trend data for charts
    registration_trend_labels = [str(date) for date in dates]
    registration_trend_data = [int(count) for count in counts]

    # Get religion distribution
    religions = ['Islam', 'Kristen', 'Katolik', 'Hindu', 'Buddha', 'Konghucu', 'Lainnya']
    religion_counts = []
    for religion in religions:
        count = len([f for f in forms if f.religion == religion])
        religion_counts.append(count)

    return render_template('dashboard_admin.html',
        total_applicants=total_applicants,
        accepted_count=accepted_count,
        rejected_count=rejected_count,
        pending_count=pending_count,
        payment_verified_count=payment_verified_count,
        daily_increase=daily_increase,
        registration_dates=dates,
        registration_counts=counts,
        major_counts=list(major_counts.values()),
        major_names=major_names,
        recent_forms=recent_forms,
        datetime=datetime,
        registration_trend_labels=registration_trend_labels,
        registration_trend_data=registration_trend_data,
        gender_counts=gender_counts,
        religion_counts=religion_counts
    )

@main.route('/get_applicants_data')
@login_required
def get_applicants_data():
    if not current_user.role == 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
        
    forms = Form.query.all()
    data = []
    
    for form in forms:
        major_names = {
            'tkj': 'Teknik Komputer dan Jaringan',
            'rpl': 'Rekayasa Perangkat Lunak',
            'mm': 'Multimedia'
        }
        
        track_names = {
            'achievement': 'Prestasi',
            'affirmation': 'Afirmasi',
            'domicile': 'Zonasi'
        }
        
        status_display = {
            'pending': 'Menunggu Verifikasi',
            'accepted': 'Diterima',
            'rejected': 'Ditolak'
        }
        
        payment_status_display = {
            'verified': 'Terverifikasi',
            'submitted': 'Menunggu Verifikasi',
            None: 'Belum Dibayar'
        }
        
        data.append({
            'id': form.id,
            'full_name': form.full_name or form.user.name,
            'major': major_names.get(form.major, ''),
            'previous_school': form.previous_school or '-',
            'registration_track': track_names.get(form.registration_track, 'Reguler'),
            'status': status_display.get(form.status, form.status),
            'payment_status': payment_status_display.get(form.payment_status, '-') if form.status == 'accepted' else '-',
            'timestamp': form.timestamp.strftime('%d-%m-%Y %H:%M') if form.timestamp else '-',
            'actions': render_template('components/table_actions.html', form=form)
        })
    
    return jsonify({
        'data': data
    })

@main.route('/admin/detail/<int:student_id>')
@login_required
def student_detail(student_id):
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('main.dashboard'))
        
    form = Form.query.get_or_404(student_id)    # Get all documents associated with the student that have data
    documents = []
    if form.graduation_certificate_data:
        documents.append(('graduation_certificate', 'Ijazah/SKL', form.graduation_certificate_data, form.graduation_certificate_mimetype))
    if form.birth_certificate_data:
        documents.append(('birth_certificate', 'Akta Kelahiran', form.birth_certificate_data, form.birth_certificate_mimetype))
    if form.family_card_data:
        documents.append(('family_card', 'Kartu Keluarga', form.family_card_data, form.family_card_mimetype))
    if form.report_card_data:
        documents.append(('report_card', 'Rapor', form.report_card_data, form.report_card_mimetype))
    if form.photo_data:
        documents.append(('photo', 'Pas Foto', form.photo_data, form.photo_mimetype))
    if form.payment_proof_data:
        documents.append(('payment_proof', 'Bukti Pembayaran', form.payment_proof_data, form.payment_proof_mimetype))
    
    return render_template('admin/student_detail.html', 
                         student=form,
                         documents=documents,
                         datetime=datetime)
