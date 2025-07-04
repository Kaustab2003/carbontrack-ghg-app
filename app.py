from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from datetime import datetime
from io import BytesIO
import pyotp
from flask_caching import Cache
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy
from utils.pdf_utils import generate_pdf



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'your_salt_here')

# Step 1: Add SQLite Database Support
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbontrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User and History models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    two_fa_secret = db.Column(db.String(100), nullable=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    username = db.Column(db.String(80))
    industry = db.Column(db.String(100))
    emission_type = db.Column(db.String(50)) 
    emission_data = db.Column(db.Float)
    energy_consumption = db.Column(db.Float)
    waste_production = db.Column(db.Float)
    water_consumption = db.Column(db.Float)
    facility_size = db.Column(db.Float)
    prediction = db.Column(db.Float)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
model = joblib.load('model/emission_model.pkl')

EMAIL_CONFIG = {
    'sender': os.getenv('EMAIL_SENDER', 'your_email@example.com'),
    'password': os.getenv('EMAIL_PASSWORD', 'your_email_password'),
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.example.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587))
}

# Save and get predictions using SQLAlchemy DB instead of CSV
def save_prediction(username, data):
    record = History(
        timestamp=data['timestamp'],
        username=username,
        industry=data['industry'],
        emission_type=data.get("emission_type", "carbon_dioxide"),
        emission_data=data['emission_data'],
        energy_consumption=data['energy_consumption'],
        waste_production=data['waste_production'],
        water_consumption=data['water_consumption'],
        facility_size=data['facility_size'],
        prediction=data['prediction']
    )
    db.session.add(record)
    db.session.commit()


def get_user_history(username):
    records = History.query.filter_by(username=username).all()
    return pd.DataFrame([{
        'timestamp': r.timestamp,
        'industry': r.industry,
        'emission_type': r.emission_type,
        'emission_data': r.emission_data,
        'energy_consumption': r.energy_consumption,
        'waste_production': r.waste_production,
        'water_consumption': r.water_consumption,
        'facility_size': r.facility_size,
        'prediction': r.prediction
    } for r in records])



# Step 3: Use SQLAlchemy DB for user registration/login
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def create_user(username, password, email):
    hashed_pw = generate_password_hash(password)
    user = User(username=username, password=hashed_pw, email=email)
    db.session.add(user)
    db.session.commit()

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(0, 255, 0)
    pdf.cell(200, 10, txt=" GHG Emission Prediction Report", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.ln(10)

    for key, value in data.items():
        label = key.replace("_", " ").title()
        pdf.cell(200, 10, txt=f"{label}: {value}", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(180, 180, 180)
    pdf.ln(5)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # ✔️ Use dest='S' to output as string, then encode and wrap in BytesIO
    buffer = BytesIO()
    pdf.output(buffer, dest='F')  # 'F' writes to file-like object
    buffer.seek(0)
    return buffer

...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/predict', methods=['GET'])
def predict_form():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        scaler = joblib.load("model/scaler.pkl")
        feature_names = joblib.load("model/feature_names.pkl")

        industry = request.form.get("industry", "Manufacturing")
        emission_type = request.form.get("emission_type", "carbon_dioxide")
        emission_data = float(request.form["emission_data"])
        energy = float(request.form["energy_consumption"])
        waste = float(request.form["waste_production"])
        water = float(request.form["water_consumption"])
        area = float(request.form["facility_size"])

        input_data = pd.DataFrame([[energy, waste, water, area]], columns=feature_names)
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]

        prediction_id = datetime.now().isoformat()

        if "username" in session:
            save_prediction(session["username"], {
                "industry": industry,
                "emission_type": emission_type,
                "emission_data": emission_data,
                "energy_consumption": energy,
                "waste_production": waste,
                "water_consumption": water,
                "facility_size": area,
                "prediction": prediction,
                "timestamp": prediction_id
            })
            session["last_prediction_id"] = prediction_id

        return render_template("result.html", 
                               prediction=round(prediction, 2), 
                               emission_data=emission_data,
                               prediction_id=prediction_id,
                               emission_type=emission_type)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/generate_pdf/<prediction_id>')
def generate_pdf_report(prediction_id):
    if 'username' not in session:
        flash("You must be logged in to generate PDF reports.")
        return redirect(url_for('login'))

    try:
        history = get_user_history(session['username'])
        
        print("Raw user history:", history) 
        match = history[history['timestamp'] == prediction_id]
        if match.empty:
            return "Prediction not found.", 404

        prediction_data = match.iloc[0].to_dict()
        print("Prediction data to be used in PDF:", prediction_data)
        print("Prediction data to be used in PDF:", prediction_data)
        pdf_stream = generate_pdf(prediction_data)
        return send_file(pdf_stream, mimetype='application/pdf', as_attachment=True, download_name='prediction_report.pdf')

    except Exception as e:
        print("PDF generation error:", str(e)) 
        return f"An error occurred while generating PDF: {e}", 500






@app.route('/email_results/<prediction_id>', methods=['GET', 'POST'])
def email_results(prediction_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = request.form['email']
        history = get_user_history(session['username'])
        prediction_data = history[history['timestamp'] == prediction_id].iloc[0].to_dict()
        try:
            pdf_bytes = generate_pdf(prediction_data)
            send_email(
                email,
                "Your GHG Emission Prediction Report",
                f"Please find attached your report.\nPredicted CO₂ Emissions: {prediction_data['prediction']} tons/year",
                attachment=pdf_bytes
            )
            flash('Email sent successfully!')
        except Exception as e:
            flash(f'Failed to send email: {str(e)}')
        return redirect(url_for('dashboard'))
    return render_template('email_form.html', prediction_id=prediction_id)

@app.route('/batch_predict', methods=['GET', 'POST'])
def batch_predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash("Please upload a valid CSV file.")
            return redirect(request.url)

        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip().str.lower()

            scaler = joblib.load("model/scaler.pkl")
            feature_names = joblib.load("model/feature_names.pkl")

            required = ['industry', 'emission_data'] + feature_names
            missing_cols = [col for col in required if col not in df.columns]
            if missing_cols:
                flash(f"⚠️ Missing columns in CSV: {', '.join(missing_cols)}")
                return redirect(request.url)

            input_data = df[feature_names]
            valid_input_data = input_data.dropna()
            skipped_rows = len(input_data) - len(valid_input_data)

            if skipped_rows > 0:
                flash(f"⚠️ Skipped {skipped_rows} row(s) due to missing values in required columns.")

            scaled_input = scaler.transform(valid_input_data)
            df.loc[valid_input_data.index, 'prediction'] = model.predict(scaled_input)

            for _, row in df.iterrows():
                row_data = row.to_dict()
                row_data["timestamp"] = datetime.now().isoformat()
                save_prediction(session['username'], row_data)

            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name='batch_predictions.csv')

        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect(request.url)

    return render_template("batch_predict.html")

@app.route('/visualization')
@cache.cached(timeout=60, query_string=True)
def visualization():
    if 'username' not in session:
        return redirect(url_for('login'))

    history = get_user_history(session['username'])

    if history.empty or 'timestamp' not in history.columns or 'prediction' not in history.columns:
        flash("No prediction history available for visualization.")
        return redirect(url_for('dashboard'))

    return render_template('visualization.html', history=history)
@app.route('/history')
def view_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    records = History.query.filter_by(username=session['username']).all()

    history = pd.DataFrame([{
        'timestamp': r.timestamp,
        'industry': r.industry,
        'emission_type': r.emission_type,
        'emission_data': r.emission_data,
        'energy_consumption': r.energy_consumption,
        'waste_production': r.waste_production,
        'water_consumption': r.water_consumption,
        'facility_size': r.facility_size,
        'prediction': r.prediction
    } for r in records])

    return render_template('history.html', history=history)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        if user.two_fa_secret:
            session['temp_username'] = username
            return redirect(url_for('verify_2fa'))

        session['username'] = username
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash("User not found.")
        return redirect(url_for('dashboard'))

    user_info = {
        'username': user.username,
        'email': user.email,
        'two_fa_enabled': bool(user.two_fa_secret)
    }

    return render_template('profile.html', user_info=user_info)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


...

# End of file
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
