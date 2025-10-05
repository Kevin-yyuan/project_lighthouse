import pandas as pd
import sqlite3
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# --- Configuration ---
DB_FILE_PATH = 'lighthouse.db'

# --- 1. Load Data from Database ---
def load_data_from_db(db_path):
    print("Loading data from normalized database...")
    with sqlite3.connect(db_path) as conn:
        query = '''
            SELECT p.ProjectID, p.ProjectType, p.ProjectStatus, p.Budget, 
                   p.ScheduleVariance_Days, p.BudgetVariance_CAD,
                   prop.City, v.VendorName as Vendor
            FROM projects p
            JOIN properties prop ON p.PropertyID = prop.PropertyID
            JOIN vendors v ON p.VendorID = v.VendorID
        '''
        df = pd.read_sql_query(query, conn)
        # Convert data types for modeling
        df['ScheduleVariance_Days'] = pd.to_numeric(df['ScheduleVariance_Days'])
        df['BudgetVariance_CAD'] = pd.to_numeric(df['BudgetVariance_CAD'])
        df['Budget'] = pd.to_numeric(df['Budget'])
        return df

# --- 2. Prepare Data and Train Model ---
def train_risk_model(df):
    print("Training project risk model with RandomForestClassifier...")
    train_df = df[df['ProjectStatus'] == 'Completed'].copy()
    train_df['IsAtRisk'] = ((train_df['ScheduleVariance_Days'] > 15) | (train_df['BudgetVariance_CAD'] > 0)).astype(int)
    # We only drop rows for training where the target is known. 
    # For prediction, we will impute missing budget values.
    train_df.dropna(subset=['ProjectType', 'Vendor', 'Budget', 'City', 'IsAtRisk'], inplace=True)

    if len(train_df) < 10: return None

    features = ['ProjectType', 'Vendor', 'Budget', 'City']
    X = train_df[features]
    y = train_df['IsAtRisk']

    # Define preprocessing pipelines for different feature types
    categorical_features = ['ProjectType', 'Vendor', 'City']
    numeric_features = ['Budget']

    numeric_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='median'))])
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])

    model_pipeline.fit(X, y)
    print("Model training complete.")
    return model_pipeline, features

# --- 3. Predict and Explain Risk ---
def predict_and_explain_risk(df, model_pipeline, features):
    if model_pipeline is None: return None

    print("Predicting risk for ongoing and future projects...")
    predict_df = df[df['ProjectStatus'].isin(['In Progress', 'Not Started'])].copy()
    if predict_df.empty: return None

    X_predict = predict_df[features]
    risk_scores = model_pipeline.predict_proba(X_predict)[:, 1]

    def map_score_to_risk(score):
        if score > 0.7: return "High"
        elif score > 0.4: return "Medium"
        else: return "Low"

    predictions = pd.DataFrame({
        'ProjectID': predict_df['ProjectID'],
        'RiskScore': risk_scores,
        'PredictedRisk': [map_score_to_risk(s) for s in risk_scores]
    })
    predictions['RiskScore'] = predictions['RiskScore'].round(4)
    print(f"Generated {len(predictions)} new risk predictions.")

    # --- SHAP EXPLAINABILITY ---
    print("Calculating feature contributions with SHAP...")
    preprocessor = model_pipeline.named_steps['preprocessor']
    classifier = model_pipeline.named_steps['classifier']
    
    X_predict_transformed = preprocessor.transform(X_predict)

    if hasattr(X_predict_transformed, "toarray"):
        X_predict_transformed = X_predict_transformed.toarray()

    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(X_predict_transformed)

    feature_names = preprocessor.get_feature_names_out()
    
    # Correctly slice the shap_values array for the positive class (class 1)
    shap_df = pd.DataFrame(shap_values[:, :, 1], columns=feature_names)

    # Find the primary risk factor for each prediction
    primary_factors = shap_df.abs().idxmax(axis=1).str.replace('cat__', '').str.replace('num__', '')
    predictions['PrimaryRiskFactor'] = primary_factors.values
    print("SHAP analysis complete.")

    return predictions

# --- 4. Update Database ---
def update_database_with_predictions(predictions_df, db_path):
    if predictions_df is None or predictions_df.empty: return

    print(f"Updating {len(predictions_df)} projects in the database...")
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE projects SET RiskScore = NULL, PredictedRisk = NULL, PrimaryRiskFactor = NULL")
            
            update_query = '''
                UPDATE projects
                SET RiskScore = ?, PredictedRisk = ?, PrimaryRiskFactor = ?
                WHERE ProjectID = ?
            '''
            cursor.executemany(update_query, [
                (row['RiskScore'], row['PredictedRisk'], row['PrimaryRiskFactor'], row['ProjectID'])
                for index, row in predictions_df.iterrows()
            ])
            conn.commit()
        print("Database updated successfully.")
    except Exception as e:
        print(f"An error occurred during database update: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    full_df = load_data_from_db(DB_FILE_PATH)
    model, features = train_risk_model(full_df)
    predictions = predict_and_explain_risk(full_df, model, features)
    update_database_with_predictions(predictions, DB_FILE_PATH)
    print("Prediction and explanation process completed.")