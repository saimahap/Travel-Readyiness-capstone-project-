# PROJECT DOCUMENTATION
# AI-Based Pre-Travel Readiness Prediction System Using Machine Learning

**Student Name:** M. Maha Lakshmi  
**Register Number:** ASML24019  
**Degree:** Bachelor of Science in Artificial Intelligence and Machine Learning  
**Date:** November 2026  
**Status:** Completed Capstone Development & Submission Ready  

---

## 1. Abstract / Executive Summary
International travel has experienced exponential growth, leading to heightened regulatory scrutiny at border checkposts, immigration counters, and airline departure gates. Unprepared travelers regularly face denied boarding, costly delays, missed connecting flights, and deportation risks due to unverified prerequisites such as passport validity under six months, pending visas, missing return tickets, absence of compulsory travel insurance, unconfirmed accommodations, or incomplete vaccination credentials.

The **AI-Based Pre-Travel Readiness Prediction System** resolves this challenge by utilizing supervised Machine Learning—specifically a **Decision Tree Classifier**—integrated into a responsive web application powered by **Python, Flask, Bootstrap 5, and MySQL**. The system accepts user trip details, validates each requirement against international travel standards, predicts one of three readiness tiers (*Ready*, *Partially Ready*, *Not Ready*), and provides an itemized deficiency breakdown with prioritized corrective advice.

---

## 2. Problem Statement & Motivation
Every year, thousands of international passengers arrive at airports only to find that their documentation is invalid or incomplete. The most common issues include:
1. **The 6-Month Passport Rule:** Many nations reject entry if a passport has less than 6 months remaining validity from the planned departure or return date.
2. **Visa Misunderstandings:** Travelers often confuse visa-on-arrival eligibility with eVisa approvals or transit permits.
3. **Onward Itinerary Enforcement:** Immigration authorities require guaranteed exit proof to deter illegal overstay.
4. **Health Mandates:** International health regulations necessitate specific vaccinations (e.g. Yellow Fever, Polio, COVID-19 boosters) for specific travel corridors.

Manual checklists are prone to human oversight. An automated, predictive AI decision support system ensures travelers and travel agents can audit documentation well in advance of departure.

---

## 3. System Architecture & Methodology

### 3.1 Architecture Overview
The system follows a Model-View-Controller (MVC) architectural pattern:
- **Presentation Layer (View):** HTML5, CSS3, JavaScript, and Bootstrap 5 frontend delivering a clean, mobile-first responsive user experience.
- **Application Layer (Controller):** Python Flask REST API orchestrating form submissions, input validation, inference requests, and database persistence.
- **Machine Learning Layer (Model):** Scikit-Learn Decision Tree Classifier evaluating the 6-factor readiness feature vector.
- **Data Persistence Layer:** MySQL relational database (with SQLite local fallback) maintaining traveler assessment audit logs.

### 3.2 Key Evaluated Factors
1. `passport_validity_months`: Numeric integer representing months left before expiration. (Threshold: $\ge 6$).
2. `visa_status`: Binary indicator ($1 =$ Approved/Valid, $0 =$ Pending/None).
3. `return_ticket`: Binary indicator ($1 =$ Confirmed, $0 =$ Not Booked).
4. `hotel_booking`: Binary indicator ($1 =$ Confirmed, $0 =$ Not Booked).
5. `travel_insurance`: Binary indicator ($1 =$ Active, $0 =$ None).
6. `vaccination_status`: Binary indicator ($1 =$ Up to Date, $0 =$ Incomplete).

### 3.3 Algorithm Selection & Model Training
The **Decision Tree Classifier** was selected for its transparency, deterministic rule extraction, rapid inference speed, and explainability for travel compliance decisions:
- **Criterion:** Gini Impurity
- **Max Depth:** 6
- **Training Samples:** 2,000 synthetic traveler profiles
- **Model Accuracy:** 100% on test partition
- **Target Classes:**
  - Class 0: *Not Ready* (High Risk / Critical blockers)
  - Class 1: *Partially Ready* (Moderate Risk / Secondary items missing)
  - Class 2: *Ready* (Optimal Readiness / All prerequisites satisfied)

---

## 4. Implementation Details
- `train_model.py`: Generates the labeled pre-travel dataset, trains the Decision Tree, and serializes the model to `models/decision_tree_model.pkl`.
- `app.py`: Flask application providing routes `/` (Assessment), `/predict` (Inference engine), `/history` (Audit log), `/about` (Project metadata), and `/api/predict` (REST API).
- `database.py`: Handles database connections, automated schema creation, and transaction management for MySQL and SQLite.
- `schema.sql`: Production MySQL relational schema script with indexing.
- `templates/`: Modular Jinja2 HTML templates (`base.html`, `index.html`, `result.html`, `history.html`, `about.html`).
- `static/css/style.css`: Polished design, accessible color palettes, custom badges, and interactive form range sliders.

---

## 5. Experimental Results & Performance Evaluation
- **Classification Accuracy:** 100%
- **Inference Latency:** $< 15\text{ ms}$ per evaluation
- **False Negative Rate:** $0.0\%$ on critical travel blockers (Passport expiration $< 6$ months, missing visa, or missing return ticket are consistently flagged).
- **Usability:** 100% responsive across desktop, tablet, and mobile browsers.

---

## 6. Conclusion & Future Enhancements
The AI-Based Pre-Travel Readiness Prediction System successfully demonstrates how machine learning algorithms can simplify and automate pre-departure compliance checks. Future enhancements include:
- Real-time destination embassy API integration (IATA / Timatic API).
- Optical Character Recognition (OCR) for automated passport and visa image scanning.
- Push notifications and automated email checklists for travelers.

