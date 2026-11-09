import os
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def generate_travel_dataset(n_samples=2500, random_state=42):
    """
    Generates a realistic travel preparedness dataset with 6 core readiness factors:
    1. passport_valid (1 = Valid and >=6 months remaining, 0 = Expired or <6 months)
    2. visa_available (1 = Approved/Visa-free, 0 = Pending/Not obtained)
    3. return_ticket (1 = Confirmed, 0 = Not booked)
    4. hotel_booking (1 = Confirmed, 0 = Not booked)
    5. travel_insurance (1 = Active, 0 = None)
    6. vaccination_status (1 = Completed, 0 = Incomplete)
    
    Target:
    1: 'Ready to Travel'
    0: 'Not Ready to Travel'
    """
    np.random.seed(random_state)
    
    passport_valid = np.random.choice([1, 0], size=n_samples, p=[0.82, 0.18])
    visa_available = np.random.choice([1, 0], size=n_samples, p=[0.80, 0.20])
    return_ticket = np.random.choice([1, 0], size=n_samples, p=[0.85, 0.15])
    hotel_booking = np.random.choice([1, 0], size=n_samples, p=[0.75, 0.25])
    travel_insurance = np.random.choice([1, 0], size=n_samples, p=[0.65, 0.35])
    vaccination_status = np.random.choice([1, 0], size=n_samples, p=[0.80, 0.20])
    
    labels = []
    scores = []
    
    for i in range(n_samples):
        pv = passport_valid[i]
        va = visa_available[i]
        rt = return_ticket[i]
        hb = hotel_booking[i]
        ti = travel_insurance[i]
        vs = vaccination_status[i]
        
        # Calculate readiness score (0 - 100)
        score = (pv * 25) + (va * 25) + (rt * 20) + (hb * 10) + (ti * 10) + (vs * 10)
        scores.append(score)
        
        # Critical blockers: Passport invalid/under 6mo, No Visa, or No Return Ticket
        if pv == 0 or va == 0 or rt == 0:
            labels.append(0)  # Not Ready to Travel
        elif score >= 70:
            labels.append(1)  # Ready to Travel
        else:
            labels.append(0)  # Not Ready to Travel
            
    df = pd.DataFrame({
        'passport_valid': passport_valid,
        'visa_available': visa_available,
        'return_ticket': return_ticket,
        'hotel_booking': hotel_booking,
        'travel_insurance': travel_insurance,
        'vaccination_status': vaccination_status,
        'readiness_score': scores,
        'target': labels
    })
    
    return df

def train_and_export():
    print("Generating comprehensive travel readiness dataset...")
    df = generate_travel_dataset(n_samples=3000)
    
    os.makedirs('dataset', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    csv_path = os.path.join('dataset', 'travel_readiness_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully saved to: {csv_path}")
    
    feature_cols = [
        'passport_valid',
        'visa_available',
        'return_ticket',
        'hotel_booking',
        'travel_insurance',
        'vaccination_status'
    ]
    X = df[feature_cols]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\nTraining Decision Tree Classifier...")
    model = DecisionTreeClassifier(
        criterion='gini',
        max_depth=5,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Training Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Ready to Travel', 'Ready to Travel']))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model artifact
    model_bundle = {
        'model': model,
        'features': feature_cols,
        'classes': {0: 'Not Ready to Travel', 1: 'Ready to Travel'},
        'accuracy': float(accuracy)
    }
    
    model_path = os.path.join('models', 'decision_tree_model.pkl')
    joblib.dump(model_bundle, model_path)
    print(f"\nModel bundle saved to: {model_path}")

if __name__ == '__main__':
    train_and_export()

