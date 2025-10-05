import pandas as pd
import sqlite3
import shap
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np
from datetime import datetime

# --- Configuration ---
DB_FILE_PATH = 'lighthouse.db'

# --- 1. Load Data from Database ---


def load_data_from_db(db_path):
    print("Loading data from normalized database...")
    with sqlite3.connect(db_path) as conn:
        query = '''
            SELECT p.ProjectID, p.ProjectType, p.ProjectStatus, p.Budget, 
                   p.ActualCost, p.StartDate, p.PlannedEndDate, p.ActualEndDate,
                   p.ScheduleVariance_Days, p.BudgetVariance_CAD,
                   prop.City, v.VendorName as Vendor
            FROM projects p
            JOIN properties prop ON p.PropertyID = prop.PropertyID
            JOIN vendors v ON p.VendorID = v.VendorID
        '''
        df = pd.read_sql_query(query, conn)
        # Convert data types for modeling
        df['ScheduleVariance_Days'] = pd.to_numeric(
            df['ScheduleVariance_Days'])
        df['BudgetVariance_CAD'] = pd.to_numeric(df['BudgetVariance_CAD'])
        df['Budget'] = pd.to_numeric(df['Budget'])
        df['ActualCost'] = pd.to_numeric(df['ActualCost'])

        # Calculate actual project duration for completed projects
        df['ActualDuration_Days'] = None
        completed_mask = (df['ProjectStatus'] == 'Completed') & df['StartDate'].notna(
        ) & df['ActualEndDate'].notna()
        if completed_mask.any():
            start_dates = pd.to_datetime(df.loc[completed_mask, 'StartDate'])
            end_dates = pd.to_datetime(df.loc[completed_mask, 'ActualEndDate'])
            df.loc[completed_mask, 'ActualDuration_Days'] = (
                end_dates - start_dates).dt.days

        # Calculate planned duration for all projects
        df['PlannedDuration_Days'] = None
        planned_mask = df['StartDate'].notna() & df['PlannedEndDate'].notna()
        if planned_mask.any():
            start_dates = pd.to_datetime(df.loc[planned_mask, 'StartDate'])
            planned_dates = pd.to_datetime(
                df.loc[planned_mask, 'PlannedEndDate'])
            df.loc[planned_mask, 'PlannedDuration_Days'] = (
                planned_dates - start_dates).dt.days

        return df

# --- 2. Train Risk Classification Model ---


def train_risk_model(df):
    print("Training project risk model with RandomForestClassifier...")
    train_df = df[df['ProjectStatus'] == 'Completed'].copy()
    train_df['IsAtRisk'] = ((train_df['ScheduleVariance_Days'] > 15) | (
        train_df['BudgetVariance_CAD'] > 0)).astype(int)
    train_df.dropna(subset=['ProjectType', 'Vendor',
                    'Budget', 'City', 'IsAtRisk'], inplace=True)

    if len(train_df) < 10:
        return None

    features = ['ProjectType', 'Vendor', 'Budget', 'City']
    X = train_df[features]
    y = train_df['IsAtRisk']

    categorical_features = ['ProjectType', 'Vendor', 'City']
    numeric_features = ['Budget']

    numeric_transformer = Pipeline(
        steps=[('imputer', SimpleImputer(strategy='median'))])
    categorical_transformer = Pipeline(
        steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=100, random_state=42, class_weight='balanced'))
    ])

    model_pipeline.fit(X, y)
    print("Risk model training complete.")
    return model_pipeline, features

# --- 3. Train Cost Prediction Model ---


def train_cost_model(df):
    print("Training cost prediction model with RandomForestRegressor...")
    train_df = df[df['ProjectStatus'] == 'Completed'].copy()
    train_df.dropna(subset=['ProjectType', 'Vendor',
                    'Budget', 'City', 'ActualCost'], inplace=True)

    if len(train_df) < 10:
        print("Not enough data for cost model training.")
        return None

    features = ['ProjectType', 'Vendor', 'Budget', 'City']
    X = train_df[features]
    y = train_df['ActualCost']

    categorical_features = ['ProjectType', 'Vendor', 'City']
    numeric_features = ['Budget']

    numeric_transformer = Pipeline(
        steps=[('imputer', SimpleImputer(strategy='median'))])
    categorical_transformer = Pipeline(
        steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    model_pipeline.fit(X, y)

    # Evaluate model performance
    y_pred = model_pipeline.predict(X)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    print(f"Cost model training complete. MAE: ${mae:,.2f}, R²: {r2:.3f}")

    return model_pipeline, features

# --- 4. Train Duration Prediction Model ---


def train_duration_model(df):
    print("Training duration prediction model with RandomForestRegressor...")
    train_df = df[df['ProjectStatus'] == 'Completed'].copy()
    train_df.dropna(subset=['ProjectType', 'Vendor', 'Budget', 'City',
                    'ActualDuration_Days', 'PlannedDuration_Days'], inplace=True)

    if len(train_df) < 10:
        print("Not enough data for duration model training.")
        return None

    features = ['ProjectType', 'Vendor',
                'Budget', 'City', 'PlannedDuration_Days']
    X = train_df[features]
    y = train_df['ActualDuration_Days']

    categorical_features = ['ProjectType', 'Vendor', 'City']
    numeric_features = ['Budget', 'PlannedDuration_Days']

    numeric_transformer = Pipeline(
        steps=[('imputer', SimpleImputer(strategy='median'))])
    categorical_transformer = Pipeline(
        steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    model_pipeline.fit(X, y)

    # Evaluate model performance
    y_pred = model_pipeline.predict(X)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    print(
        f"Duration model training complete. MAE: {mae:.1f} days, R²: {r2:.3f}")

    return model_pipeline, features

# --- 5. Make Predictions ---


def make_predictions(df, risk_model, cost_model, duration_model, risk_features, cost_features, duration_features):
    print("Making predictions for ongoing and future projects...")
    predict_df = df[df['ProjectStatus'].isin(
        ['In Progress', 'Not Started'])].copy()
    if predict_df.empty:
        print("No projects to predict.")
        return None

    predictions = pd.DataFrame({'ProjectID': predict_df['ProjectID']})

    # Risk predictions
    if risk_model is not None:
        X_risk = predict_df[risk_features]
        risk_scores = risk_model.predict_proba(X_risk)[:, 1]

        def map_score_to_risk(score):
            if score > 0.7:
                return "High"
            elif score > 0.4:
                return "Medium"
            else:
                return "Low"

        predictions['RiskScore'] = risk_scores.round(4)
        predictions['PredictedRisk'] = [
            map_score_to_risk(s) for s in risk_scores]

    # Cost predictions
    if cost_model is not None:
        X_cost = predict_df[cost_features]
        predicted_costs = cost_model.predict(X_cost)
        predictions['PredictedCost'] = predicted_costs.round(2)

    # Duration predictions
    if duration_model is not None:
        X_duration = predict_df[duration_features]
        predicted_durations = duration_model.predict(X_duration)
        predictions['PredictedDuration_Days'] = predicted_durations.round(
            0).astype(int)

    print(f"Generated predictions for {len(predictions)} projects.")
    return predictions

# --- 6. Update Database ---


def update_database_with_predictions(db_path, predictions):
    if predictions is None or predictions.empty:
        print("No predictions to update.")
        return

    print(f"Updating {len(predictions)} projects in the database...")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Add new columns if they don't exist
        try:
            cursor.execute(
                "ALTER TABLE projects ADD COLUMN PredictedCost REAL")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            cursor.execute(
                "ALTER TABLE projects ADD COLUMN PredictedDuration_Days INTEGER")
        except sqlite3.OperationalError:
            pass  # Column already exists

        for _, row in predictions.iterrows():
            update_query = "UPDATE projects SET "
            update_values = []
            params = []

            if 'RiskScore' in row and pd.notna(row['RiskScore']):
                update_values.append("RiskScore = ?")
                params.append(row['RiskScore'])

            if 'PredictedRisk' in row and pd.notna(row['PredictedRisk']):
                update_values.append("PredictedRisk = ?")
                params.append(row['PredictedRisk'])

            if 'PredictedCost' in row and pd.notna(row['PredictedCost']):
                update_values.append("PredictedCost = ?")
                params.append(row['PredictedCost'])

            if 'PredictedDuration_Days' in row and pd.notna(row['PredictedDuration_Days']):
                update_values.append("PredictedDuration_Days = ?")
                params.append(row['PredictedDuration_Days'])

            if update_values:
                update_query += ", ".join(update_values) + \
                    " WHERE ProjectID = ?"
                params.append(row['ProjectID'])
                cursor.execute(update_query, params)

        conn.commit()
        print("Database updated successfully.")


# --- Main Execution ---
if __name__ == '__main__':
    # Load data
    df = load_data_from_db(DB_FILE_PATH)

    # Train models
    risk_model, risk_features = train_risk_model(df) if len(
        df[df['ProjectStatus'] == 'Completed']) > 0 else (None, None)
    cost_model, cost_features = train_cost_model(df) if len(
        df[df['ProjectStatus'] == 'Completed']) > 0 else (None, None)
    duration_model, duration_features = train_duration_model(df) if len(
        df[df['ProjectStatus'] == 'Completed']) > 0 else (None, None)

    # Make predictions
    predictions = make_predictions(df, risk_model, cost_model, duration_model,
                                   risk_features, cost_features, duration_features)

    # Update database
    update_database_with_predictions(DB_FILE_PATH, predictions)

    print("Enhanced prediction process completed.")
