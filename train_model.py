import os
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def generate_synthetic_travel_data(n_samples=1500, random_state=42):
    """
    Generate synthetic dataset for travel readiness prediction based on 6 core criteria:
    - passport_validity_months (integer)
    - visa_status (1 = Approved / Not Required, 0 = Pending / Rejected / None)
    - return_ticket (1 = Confirmed, 0 = Not Booked)
    - hotel_booking (1 = Confirmed, 0 = Not Booked)
    - travel_insurance (1 = Purchased, 0 = None)
    - vaccination_status (1 = Fully Vaccinated / Compliant, 0 = Incomplete / None)
    
    Target:
    - 2: "Ready" (High readiness, all or virtually all requirements met)
    - 1: "Partially Ready" (Moderate readiness, essential items met but non-critical items missing)
    - 0: "Not Ready" (Critical travel blocker present: expired/short passport, no visa, no ticket)
    """
    np.random.seed(random_state)
    
    passport_months = np.random.randint(0, 36, size=n_samples)
    visa_status = np.random.choice([0, 1], size=n_samples, p=[0.25, 0.75])
    return_ticket = np.random.choice([0, 1], size=n_samples, p=[0.20, 0.80])
    hotel_booking = np.random.choice([0, 1], size=n_samples, p=[0.25, 0.75])
    travel_insurance = np.random.choice([0, 1], size=n_samples, p=[0.40, 0.60])
    vaccination_status = np.random.choice([0, 1], size=n_samples, p=[0.20, 0.80])
    
    labels = []
    for i in range(n_samples):
        p_val = passport_months[i] >= 6  # standard international requirement: >= 6 months validity
        v_val = visa_status[i] == 1
        t_val = return_ticket[i] == 1
        h_val = hotel_booking[i] == 1
        ins_val = travel_insurance[i] == 1
        vac_val = vaccination_status[i] == 1
        
        # Critical blockers: Passport < 6 months, No Visa, or No Return Ticket
        if not p_val or not v_val or not t_val:
            labels.append(0)  # Not Ready
        elif h_val and vac_val and ins_val:
            labels.append(2)  # Fully Ready
        elif h_val and vac_val and not ins_val:
            labels.append(1)  # Partially Ready (missing insurance)
        elif not h_val or not vac_val:
            labels.append(1)  # Partially Ready (missing hotel or vaccine)
        else:
            labels.append(1)
            
    df = pd.DataFrame({
        'passport_validity_months': passport_months,
        'visa_status': visa_status,
        'return_ticket': return_ticket,
        'hotel_booking': hotel_booking,
        'travel_insurance': travel_insurance,
        'vaccination_status': vaccination_status,
        'readiness_status': labels
    })
    
    return df

def train_and_save_model():
    print("Generating synthetic travel preparedness dataset...")
    df = generate_synthetic_travel_data(n_samples=2000)
    
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    data_path = os.path.join('data', 'travel_readiness_dataset.csv')
    df.to_csv(data_path, index=False)
    print(f"Dataset saved to: {data_path}")
    
    features = [
        'passport_validity_months',
        'visa_status',
        'return_ticket',
        'hotel_booking',
        'travel_insurance',
        'vaccination_status'
    ]
    target = 'readiness_status'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Decision Tree Classifier...")
    model = DecisionTreeClassifier(
        criterion='gini',
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:")
    target_names = ['Not Ready (0)', 'Partially Ready (1)', 'Ready (2)']
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature Importances
    print("\nFeature Importances:")
    for feat, imp in zip(features, model.feature_importances_):
        print(f"  - {feat:26}: {imp:.4f}")
        
    # Save trained model and metadata
    model_bundle = {
        'model': model,
        'features': features,
        'target_names': {0: 'Not Ready', 1: 'Partially Ready', 2: 'Ready'},
        'accuracy': float(acc)
    }
    model_path = os.path.join('models', 'decision_tree_model.pkl')
    joblib.dump(model_bundle, model_path)
    print(f"\nTrained model bundle successfully exported to: {model_path}")

if __name__ == '__main__':
    train_and_save_model()

