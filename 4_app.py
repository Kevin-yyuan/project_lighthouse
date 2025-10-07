import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

# Import the chatbot service
from chatbot_service import ask_chatbot

# --- Configuration ---
DB_FILE_PATH = 'lighthouse.db'

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Helper Function to Connect to DB ---


def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE_PATH)
    return conn

# --- API Endpoint Definitions ---


@app.route('/api/ask', methods=['POST'])
def handle_ask():
    """API endpoint for the Text-to-SQL chatbot."""
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Question not provided"}), 400

    question = data['question']

    try:
        result = ask_chatbot(question)
        # Handle both old string format and new dict format
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"answer": result, "type": "text"})
    except Exception as e:
        print(f"An unexpected error occurred in the chatbot endpoint: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """API endpoint to fetch projects from the normalized database, with optional filtering."""
    try:
        query_params = request.args
        print(
            f"GET /api/projects - Request received with params: {dict(query_params)}")

        conn = get_db_connection()

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

        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()

        df = df.replace({np.nan: None})

        projects = df.to_dict(orient='records')

        return jsonify(projects)

    except Exception as e:
        print(f"GET /api/projects - An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


@app.route('/api/dashboard-analytics', methods=['GET'])
def get_dashboard_analytics():
    """API endpoint to get dashboard KPIs and analytics."""
    try:
        # For now, return a simple response until enhanced chatbot is fixed
        return jsonify({"message": "Dashboard analytics endpoint - enhanced features coming soon"})
    except Exception as e:
        print(f"GET /api/dashboard-analytics - An error occurred: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


# --- Main Execution ---
if __name__ == '__main__':
    print("Starting Flask server with chatbot endpoint...")
    print("Access the API at http://127.0.0.1:5001/api/projects")
    print("Chatbot endpoint at http://127.0.0.1:5001/api/ask")
    app.run(debug=True, port=5001)
