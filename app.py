import os
import re
from datetime import datetime
from functools import wraps
import joblib
import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# Import database and PDF generator modules
from database.db import (
    init_database, get_user_by_email, get_user_by_id,
    create_user, update_user_profile, update_user_password,
    save_assessment, get_assessment_by_id, get_user_assessments,
    get_user_assessment_stats, save_report_record, get_report_by_assessment
)
from pdf_generator import generate_pdf_report

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'travel_readiness_secret_key_aiml_2026')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Database on launch
init_database()

# Load trained Machine Learning Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'decision_tree_model.pkl')
model_bundle = None

if os.path.exists(MODEL_PATH):
    try:
        model_bundle = joblib.load(MODEL_PATH)
        print("Decision Tree Model loaded successfully into Flask.")
    except Exception as e:
        print(f"Failed to load model: {e}")
else:
    print("Warning: Trained model not found at models/decision_tree_model.pkl. Run train_ml_model.py first.")

# ----------------- Authentication Helper Decorator -----------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- Context Processors -----------------

@app.context_processor
def inject_user():
    return {
        'logged_in': 'user_id' in session,
        'current_user_name': session.get('user_name', ''),
        'current_user_email': session.get('user_email', '')
    }

# ----------------- Core Evaluation & Recommendation Engine -----------------

def evaluate_travel_readiness(form_data):
    """
    Evaluates travel readiness using both international immigration heuristics
    and the trained Scikit-learn Decision Tree Classifier.
    """
    dest = form_data.get('destination_country', 'International')
    travel_date_str = form_data.get('travel_date', '')
    expiry_date_str = form_data.get('passport_expiry_date', '')
    
    passport_avail = form_data.get('passport_status') == 'Valid'
    visa_avail = form_data.get('visa_status') in ['Approved', 'Visa-Free']
    ticket_avail = form_data.get('return_ticket') == 'Yes'
    hotel_avail = form_data.get('hotel_booking') == 'Yes'
    insurance_avail = form_data.get('travel_insurance') == 'Yes'
    vaccine_avail = form_data.get('vaccination_status') == 'Yes'
    
    # Calculate passport validity relative to travel date
    passport_valid_months = 0
    passport_meets_6mo = False
    
    try:
        t_date = datetime.strptime(travel_date_str, '%Y-%m-%d')
        exp_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        diff_days = (exp_date - t_date).days
        passport_valid_months = max(0, diff_days // 30)
        passport_meets_6mo = passport_avail and (diff_days >= 180)
    except Exception:
        passport_meets_6mo = passport_avail
        
    missing_items = []
    recommendations = []
    
    if not passport_avail:
        missing_items.append("Valid Passport")
        recommendations.append("Obtain or renew your passport prior to booking international travel.")
    elif not passport_meets_6mo:
        missing_items.append("Passport Validity >= 6 Months")
        recommendations.append("Most international authorities reject passports with less than 6 months validity. Apply for urgent renewal immediately.")
        
    if not visa_avail:
        missing_items.append("Approved Travel Visa")
        recommendations.append(f"Check the entry visa or eVisa prerequisites for {dest} and submit an application immediately.")
        
    if not ticket_avail:
        missing_items.append("Confirmed Return / Onward Ticket")
        recommendations.append("Book and confirm your return flight ticket to prevent denied boarding at the airline gate.")
        
    if not hotel_avail:
        missing_items.append("Confirmed Hotel / Accommodation")
        recommendations.append("Secure confirmed lodging or obtain an official invitation letter from your host.")
        
    if not insurance_avail:
        missing_items.append("Travel Medical Insurance")
        recommendations.append("Purchase comprehensive international travel insurance covering health, emergency evacuation, and cancellations.")
        
    if not vaccine_avail:
        missing_items.append("Mandatory Travel Vaccinations")
        recommendations.append(f"Consult WHO and embassy guidelines for {dest} to fulfill immunization requirements (e.g. Yellow Fever, COVID-19 boosters).")

    # Quantified Readiness Score (0 to 100)
    score = 0
    if passport_meets_6mo:
        score += 25
    if visa_avail:
        score += 25
    if ticket_avail:
        score += 20
    if hotel_avail:
        score += 10
    if insurance_avail:
        score += 10
    if vaccine_avail:
        score += 10

    # Decision Tree ML Inference
    pv_num = 1 if passport_meets_6mo else 0
    va_num = 1 if visa_avail else 0
    rt_num = 1 if ticket_avail else 0
    hb_num = 1 if hotel_avail else 0
    ti_num = 1 if insurance_avail else 0
    vs_num = 1 if vaccine_avail else 0
    
    features_df = pd.DataFrame([{
        'passport_valid': pv_num,
        'visa_available': va_num,
        'return_ticket': rt_num,
        'hotel_booking': hb_num,
        'travel_insurance': ti_num,
        'vaccination_status': vs_num
    }])
    
    if model_bundle:
        model = model_bundle['model']
        pred_label = int(model.predict(features_df)[0])
        prediction_result = 'Ready to Travel' if pred_label == 1 else 'Not Ready to Travel'
    else:
        # Heuristic fallback if model file is unavailable
        if pv_num == 1 and va_num == 1 and rt_num == 1 and score >= 70:
            prediction_result = 'Ready to Travel'
        else:
            prediction_result = 'Not Ready to Travel'

    return {
        'prediction_result': prediction_result,
        'readiness_score': score,
        'missing_items': missing_items,
        'recommendations': recommendations,
        'passport_meets_6mo': passport_meets_6mo,
        'passport_valid_months': passport_valid_months
    }

# ----------------- Public Routes -----------------

@app.route('/')
@app.route('/home')
@app.route('/home.html')
@app.route('/index')
@app.route('/index.html')
def home():
    return render_template('home.html')

@app.route('/about')
@app.route('/about.html')
def about():
    return render_template('about.html')

# ----------------- Authentication Routes -----------------

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation checks
        if not full_name or not email or not password:
            flash("All required fields must be completed.", "danger")
            return render_template('register.html')
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please provide a valid email address.", "danger")
            return render_template('register.html')
            
        if len(password) < 6:
            flash("Password must be at least 6 characters in length.", "danger")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match. Please re-enter.", "danger")
            return render_template('register.html')
            
        existing_user = get_user_by_email(email)
        if existing_user:
            flash("An account with this email address already exists. Please log in.", "warning")
            return redirect(url_for('login'))
            
        # Create user with secure password hash
        password_hash = generate_password_hash(password)
        user_id = create_user(full_name, email, phone, password_hash)
        
        # Log in the user immediately
        session['user_id'] = user_id
        session['user_name'] = full_name
        session['user_email'] = email
        
        flash(f"Welcome to TravelReady AI, {full_name}! Your account has been created successfully.", "success")
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            
            flash(f"Welcome back, {user['full_name']}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
@app.route('/forgot_password', methods=['GET', 'POST'])
@app.route('/forgot-password.html', methods=['GET', 'POST'])
@app.route('/forgot_password.html', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = get_user_by_email(email)
        if user:
            flash("Password reset instructions have been simulated and sent to your registered email address.", "info")
            return redirect(url_for('login'))
        else:
            flash("No account found matching this email address.", "warning")
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('home'))

# ----------------- Dashboard Route -----------------

@app.route('/dashboard')
@app.route('/dashboard.html')
@login_required
def dashboard():
    user_id = session['user_id']
    stats = get_user_assessment_stats(user_id)
    recent_assessments = get_user_assessments(user_id, limit=5)
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_assessments=recent_assessments
    )

# ----------------- Assessment & Prediction Routes -----------------

@app.route('/assessment', methods=['GET', 'POST'])
@app.route('/assessment.html', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        user_id = session['user_id']
        form_data = request.form
        
        # Run ML evaluation engine
        eval_result = evaluate_travel_readiness(form_data)
        
        assessment_record = {
            'user_id': user_id,
            'destination_country': form_data.get('destination_country', 'International').strip(),
            'travel_date': form_data.get('travel_date', ''),
            'return_date': form_data.get('return_date', ''),
            'travel_purpose': form_data.get('travel_purpose', 'Tourism'),
            'passport_status': form_data.get('passport_status', 'Invalid'),
            'passport_expiry_date': form_data.get('passport_expiry_date', ''),
            'visa_status': form_data.get('visa_status', 'None'),
            'return_ticket': form_data.get('return_ticket', 'No'),
            'hotel_booking': form_data.get('hotel_booking', 'No'),
            'travel_insurance': form_data.get('travel_insurance', 'No'),
            'vaccination_status': form_data.get('vaccination_status', 'No'),
            'prediction_result': eval_result['prediction_result'],
            'readiness_score': eval_result['readiness_score'],
            'missing_requirements': '; '.join(eval_result['missing_items']) if eval_result['missing_items'] else 'None'
        }
        
        # Save to database
        assessment_id = save_assessment(assessment_record)
        assessment_record['assessment_id'] = assessment_id
        
        # Pre-generate PDF report file
        pdf_path = generate_pdf_report(
            session.get('user_name', 'Traveler'),
            assessment_record,
            eval_result['missing_items'],
            eval_result['recommendations']
        )
        save_report_record(assessment_id, user_id, pdf_path)
        
        flash("Travel readiness assessment completed successfully!", "success")
        return redirect(url_for('result', assessment_id=assessment_id))
        
    return render_template('assessment.html')

@app.route('/result/<int:assessment_id>')
@login_required
def result(assessment_id):
    assessment_data = get_assessment_by_id(assessment_id, user_id=session['user_id'])
    if not assessment_data:
        abort(404)
        
    missing_items = [item.strip() for item in assessment_data['missing_requirements'].split(';') if item.strip() and item.strip() != 'None']
    
    # Generate recommendations dynamically for result view
    recommendations = []
    dest = assessment_data['destination_country']
    for m in missing_items:
        if 'Passport' in m:
            recommendations.append("Renew your passport immediately to ensure at least 6 months validity from departure.")
        elif 'Visa' in m:
            recommendations.append(f"Check entry visa regulations for {dest} and submit an urgent application.")
        elif 'Ticket' in m:
            recommendations.append("Book and confirm your return flight ticket to satisfy airline boarding requirements.")
        elif 'Hotel' in m:
            recommendations.append("Secure confirmed hotel bookings or obtain a formal host accommodation letter.")
        elif 'Insurance' in m:
            recommendations.append("Obtain comprehensive travel medical insurance with trip protection.")
        elif 'Vaccination' in m:
            recommendations.append(f"Complete all mandatory destination vaccinations and obtain certified certificates.")
            
    return render_template(
        'result.html',
        assessment=assessment_data,
        missing_items=missing_items,
        recommendations=recommendations
    )

@app.route('/result')
@app.route('/result.html')
def direct_result():
    """Handles direct browser navigation to /result or /result.html"""
    if 'user_id' in session:
        user_assessments = get_user_assessments(session['user_id'], limit=1)
        if user_assessments:
            return redirect(url_for('result', assessment_id=user_assessments[0]['assessment_id']))
        else:
            flash("Please complete an assessment first to view your readiness result.", "info")
            return redirect(url_for('assessment'))
    else:
        flash("Please log in or sign up to evaluate your travel readiness.", "info")
        return redirect(url_for('login'))

# ----------------- AI Report & PDF Generator Routes -----------------

@app.route('/report/<int:assessment_id>')
@login_required
def view_report(assessment_id):
    assessment_data = get_assessment_by_id(assessment_id, user_id=session['user_id'])
    if not assessment_data:
        abort(404)
        
    missing_items = [item.strip() for item in assessment_data['missing_requirements'].split(';') if item.strip() and item.strip() != 'None']
    completed_count = 6 - len(missing_items)
    completion_percentage = int((completed_count / 6.0) * 100)
    
    return render_template(
        'report.html',
        assessment=assessment_data,
        missing_items=missing_items,
        completed_count=completed_count,
        completion_percentage=completion_percentage,
        report_date=datetime.now().strftime('%Y-%m-%d')
    )

@app.route('/report')
@app.route('/report.html')
def direct_report():
    """Handles direct browser navigation to /report or /report.html"""
    if 'user_id' in session:
        user_assessments = get_user_assessments(session['user_id'], limit=1)
        if user_assessments:
            return redirect(url_for('view_report', assessment_id=user_assessments[0]['assessment_id']))
        else:
            flash("Please complete an assessment first to generate a BriefIQ report.", "info")
            return redirect(url_for('assessment'))
    else:
        flash("Please log in to generate and view BriefIQ travel reports.", "info")
        return redirect(url_for('login'))

@app.route('/download-report/<int:assessment_id>')
@login_required
def download_report(assessment_id):
    user_id = session['user_id']
    assessment_data = get_assessment_by_id(assessment_id, user_id=user_id)
    if not assessment_data:
        abort(404)
        
    missing_items = [item.strip() for item in assessment_data['missing_requirements'].split(';') if item.strip() and item.strip() != 'None']
    
    recommendations = []
    dest = assessment_data['destination_country']
    for m in missing_items:
        if 'Passport' in m:
            recommendations.append("Renew passport immediately to ensure at least 6 months validity.")
        elif 'Visa' in m:
            recommendations.append(f"Submit visa application for {dest}.")
        elif 'Ticket' in m:
            recommendations.append("Confirm return flight itinerary.")
        elif 'Hotel' in m:
            recommendations.append("Confirm lodging accommodation reservation.")
        elif 'Insurance' in m:
            recommendations.append("Obtain travel health insurance.")
        elif 'Vaccination' in m:
            recommendations.append(f"Complete required vaccinations for {dest}.")
            
    pdf_path = generate_pdf_report(
        session.get('user_name', 'Traveler'),
        assessment_data,
        missing_items,
        recommendations
    )
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"Travel_Readiness_Report_{assessment_id}.pdf",
        mimetype='application/pdf'
    )

# ----------------- History & Profile Routes -----------------

@app.route('/history')
@app.route('/history.html')
@login_required
def history():
    user_id = session['user_id']
    assessments = get_user_assessments(user_id)
    return render_template('history.html', assessments=assessments)

@app.route('/profile', methods=['GET', 'POST'])
@app.route('/profile.html', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if not full_name:
                flash("Full name cannot be left blank.", "danger")
            else:
                update_user_profile(user_id, full_name, phone)
                session['user_name'] = full_name
                flash("Profile details updated successfully.", "success")
                return redirect(url_for('profile'))
                
        elif action == 'change_password':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')
            
            if not check_password_hash(user['password_hash'], current_pwd):
                flash("The current password provided is incorrect.", "danger")
            elif len(new_pwd) < 6:
                flash("New password must be at least 6 characters in length.", "danger")
            elif new_pwd != confirm_pwd:
                flash("New passwords do not match. Please try again.", "danger")
            else:
                new_hash = generate_password_hash(new_pwd)
                update_user_password(user_id, new_hash)
                flash("Your password has been changed successfully.", "success")
                return redirect(url_for('profile'))
                
    stats = get_user_assessment_stats(user_id)
    return render_template('profile.html', user=user, stats=stats)

# ----------------- Custom 404 Error Handler -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so localhost, 127.0.0.1, and local IP work in Chrome
    print("Starting TravelReady AI server on http://localhost:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=False)
