from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField
from wtforms.validators import DataRequired
import json
from app.models import db, Form, User

main = Blueprint('main', __name__)

class AdmissionForm(FlaskForm):
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    previous_school = StringField('Previous School', validators=[DataRequired()])

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
        
        form_data = {
            'birth_date': form.birth_date.data.strftime('%Y-%m-%d'),
            'address': form.address.data,
            'phone': form.phone.data,
            'previous_school': form.previous_school.data
        }
        
        new_form = Form(
            user_id=current_user.id,
            form_data=json.dumps(form_data),  # Ensure proper JSON encoding
            status='pending'
        )
        
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