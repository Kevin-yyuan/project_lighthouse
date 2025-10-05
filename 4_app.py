import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

# --- Configuration ---
DB_FILE_PATH = 'lighthouse.db'

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Helper Function to Connect to DB ---
def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    return conn

# --- API Endpoint Definition ---
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """API endpoint to fetch projects from the normalized database, with optional filtering."""
    try:
        query_params = request.args
        print(f"GET /api/projects - Request received with params: {dict(query_params)}")

        conn = get_db_connection()
        
        # --- Dynamic Query Building ---
        base_query = '''
            SELECT
                p.ProjectID, p.ProjectType, p.ProjectStatus, p.Budget, p.ActualCost,
                p.StartDate, p.PlannedEndDate, p.ActualEndDate,
                p.ScheduleVariance_Days, p.BudgetVariance_CAD, p.ReturnOnCost_Percent,
                p.ESG_Initiative, p.PreReno_Rent, p.PostReno_Rent,
                p.RiskScore, p.PredictedRisk, p.PrimaryRiskFactor,
                prop.PropertyName,
                prop.City,
                v.VendorName as Vendor
            FROM projects p
            JOIN properties prop ON p.PropertyID = prop.PropertyID
            JOIN vendors v ON p.VendorID = v.VendorID
        '''
        
        allowed_filters = {
            'ProjectStatus': 'p.ProjectStatus',
            'City': 'prop.City',
            'ProjectType': 'p.ProjectType',
            'PredictedRisk': 'p.PredictedRisk'
        }
        
        conditions = []
        params = {}

        for key, column in allowed_filters.items():
            if key in query_params:
                conditions.append(f'{column} = :{key}')
                params[key] = query_params[key]

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        print(f"Executing query: {base_query} with params: {params}")

        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        
        # A more robust way to replace numpy NaN with Python None for JSON compatibility
        df = df.replace({np.nan: None})
        
        projects = df.to_dict(orient='records')
        
        print(f"GET /api/projects - Successfully retrieved {len(projects)} records.")
        return jsonify(projects)
    
    except Exception as e:
        print(f"GET /api/projects - An error occurred: {e}")
        return jsonify({"error": "An internal error occurred. Check server logs."}), 500

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask server with normalized database support...")
    print("Access the API at http://127.0.0.1:5000/api/projects")
    app.run(debug=True)