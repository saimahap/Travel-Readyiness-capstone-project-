# AI-Based Pre-Travel Readiness Prediction System Using Machine Learning

A complete, responsive, and functional full-stack web application developed as a Capstone Project for the **Bachelor of Science in Artificial Intelligence and Machine Learning**.

- **Student Name:** M. Maha Lakshmi  
- **Register Number:** ASML24019  
- **Domain:** Artificial Intelligence & Machine Learning  
- **Academic Year:** 2026  

---

## 🌟 Key Capabilities & Features

1. **Modern Travel & AI Themed UI:**
   - Sky blue (`#0284c7`), navy blue (`#0f172a`), and clean white aesthetic.
   - Fully responsive for desktop, tablet, and mobile with Bootstrap 5.3 and Plus Jakarta Sans typography.
   - Rounded cards, micro-badges, and interactive range/radio input components.

2. **Public Landing Experience:**
   - **Hero Section:** "Travel Smart. Travel Prepared." with instant call-to-actions.
   - **About Section:** Details on travel compliance rules, passport 6-month threshold, and methodology.
   - **Features Section:** 8 feature cards covering Passport, Visa, Return Ticket, Hotel, Insurance, Vaccination, ML Prediction, and PDF Generation.
   - **How It Works:** 4-step streamlined workflow.
   - **Contact Form & Footer:** Academic credentials, feedback form, and quick links.

3. **Secure Authentication & Session Management:**
   - User Registration (Full Name, Email, Phone, Password, Confirm Password).
   - Secure password hashing using `werkzeug.security`.
   - Login session management with `@login_required` route decorators.
   - Forgot password workflow.

4. **Personalized Traveler Dashboard:**
   - Welcome banner addressing the authenticated traveler.
   - KPI cards for Total Assessments, Ready Trips, and Not Ready Trips.
   - Interactive Doughnut chart (Chart.js) visualizing travel preparedness distribution.
   - Recent assessments table with quick links to results, interactive reports, and PDF downloads.

5. **Multi-Factor Travel Assessment Form:**
   - Destination country, departure date, return date, and travel purpose.
   - 6 Core Travel Readiness Criteria:
     1. **Passport Validity:** Date picker & automatic $\ge 6$-month threshold validation.
     2. **Visa Availability:** Approved, Visa-Free, Pending, or None.
     3. **Return Ticket:** Confirmed proof of onward itinerary.
     4. **Hotel Booking:** Confirmed accommodation reservation.
     5. **Travel Insurance:** Emergency medical & cancellation coverage.
     6. **Vaccination Status:** Destination-mandated immunization compliance.

6. **Machine Learning Prediction Engine:**
   - Trained **Decision Tree Classifier** (`sklearn.tree.DecisionTreeClassifier`) using Gini Impurity.
   - Categorizes trips into **"Ready to Travel"** or **"Not Ready to Travel"**.
   - Calculates a quantitative **Readiness Score (0% – 100%)**.
   - Identifies specific missing requirements and generates personalized remedial actions.
   - *Clear distinction between ML prediction and consular authority validation.*

7. **BriefIQ-Style AI Summary & Report Generator:**
   - Dynamic executive summary synthesized from the user's actual travel inputs.
   - Structured Metrics & KPIs table:
     - Total Requirements (6)
     - Completed Requirements
     - Missing Requirements
     - Completion Percentage
     - Readiness Status
     - Machine Learning Algorithm
     - Destination & Dates
     - Generation Timestamp
   - Native, standalone **PDF Report Generator** producing downloadable `Travel_Readiness_Report_<id>.pdf` documents.

8. **Assessment History & Audit Trail:**
   - User-isolated past travel evaluations log.
   - Direct download links for previously generated PDF reports.

9. **User Profile Management:**
   - View account details.
   - Update name and phone number.
   - Change password with existing password verification.
   - Secure logout.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js |
| **Backend** | Python 3, Flask 3.x, Jinja2, Werkzeug Security |
| **Machine Learning** | Scikit-learn (Decision Tree Classifier), Pandas, NumPy, Joblib |
| **Database** | MySQL (with automated SQLite fallback: `database/travel_readiness.db`) |
| **PDF Generation** | Pure-Python PDF 1.4 Vector Report Generator (`pdf_generator.py`) |

---

## 📂 Project Folder Structure

```
Maha Capstone project/
├── database/
│   ├── __init__.py
│   ├── db.py                           # MySQL & SQLite database connection & CRUD
│   ├── schema.sql                      # Production MySQL schema definition
│   └── travel_readiness.db             # Local SQLite database file (created automatically)
├── dataset/
│   └── travel_readiness_dataset.csv    # 3,000 synthetic traveler training samples
├── models/
│   └── decision_tree_model.pkl         # Serialized Scikit-learn Decision Tree model bundle
├── reports/
│   └── Travel_Readiness_Report_*.pdf   # Generated PDF assessment reports
├── static/
│   ├── css/
│   │   └── style.css                   # Custom theme styling & colors
│   ├── js/
│   │   └── main.js                     # Date validators, alert dismissers & tooltips
│   └── images/
├── templates/
│   ├── base.html                       # Base layout with navbar, flash alerts & footer
│   ├── home.html                       # Landing page (Hero, Features, How It Works, Contact)
│   ├── about.html                      # Academic methodology & disclaimer
│   ├── login.html                      # Authentication sign in
│   ├── register.html                   # Account registration
│   ├── forgot_password.html            # Password recovery
│   ├── dashboard.html                  # User dashboard with stats & charts
│   ├── assessment.html                 # 6-factor travel evaluation input form
│   ├── result.html                     # Prediction scorecard & recommendations
│   ├── report.html                     # BriefIQ-style AI Summary & KPIs
│   ├── history.html                    # Past evaluations table
│   └── profile.html                    # Profile management & password update
├── app.py                              # Main Flask application controller
├── pdf_generator.py                    # Standalone PDF report builder
├── train_ml_model.py                   # Dataset synthesizer & ML model trainer
├── test_app_integration.py             # Automated unit & integration test suite
├── requirements.txt                    # Python package requirements
├── PROJECT_DOCUMENTATION.md            # Complete academic documentation
└── README.md                           # Quick start and developer guide
```

---

## 🚀 Step-by-Step Installation & Setup

### 1. Environment Setup
Make sure Python 3.9+ is installed. Open a terminal or VS Code in the project directory:

```powershell
pip install -r requirements.txt
```

### 2. (Optional) Database Configuration
- By default, the application **automatically detects and connects to MySQL** if running (`travel_readiness_db` on `localhost:3306`).
- If MySQL is not running or credentials are not yet configured, the system **automatically and seamlessly switches to the local SQLite database (`database/travel_readiness.db`)**, ensuring the web application runs immediately without configuration hurdles!
- To configure MySQL credentials explicitly, you can set environment variables:
  ```powershell
  $env:MYSQL_HOST="localhost"
  $env:MYSQL_USER="root"
  $env:MYSQL_PASSWORD="your_password"
  $env:MYSQL_DB="travel_readiness_db"
  ```
  Or import `database/schema.sql` into your MySQL Workbench / phpMyAdmin.

### 3. Retrain the Machine Learning Model (Optional)
The pre-trained model bundle is already included in `models/decision_tree_model.pkl`. To retrain:
```powershell
python train_ml_model.py
```

### 4. Run the Full-Stack Web Application
Start the Flask server:
```powershell
python app.py
```

Navigate to:
```
http://127.0.0.1:5000
```

### 5. Run Automated Integration Tests
Verify all routes, registration, ML predictions, and PDF downloads:
```powershell
python test_app_integration.py
```

---

## 🎓 Academic Evaluation Checklist

- [x] Functional User Registration & Login with Password Hashing
- [x] Session Management & Protected User Routes
- [x] Interactive Landing Page with 8 Feature Cards & 4-Step Workflow
- [x] Structured 6-Factor Travel Input Form
- [x] Scikit-Learn Decision Tree Classifier ML Integration
- [x] Prediction Scorecard (Ready vs. Not Ready, 0-100% Score)
- [x] BriefIQ Dynamic Executive Summary & Metrics Table
- [x] Standalone Downloadable PDF Report Generation
- [x] Assessment History with isolated user records
- [x] User Profile editing & password change
- [x] Clean, responsive UI with Sky Blue, Navy Blue, and White theme
