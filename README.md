# Project Lighthouse: Capital Intelligence & Forecasting Hub

This project is a comprehensive, full-stack demonstration of a data analytics and intelligence solution for a fictional real estate investment firm. It showcases an end-to-end workflow, from data simulation and ETL to predictive modeling, model explainability, and a dynamic frontend dashboard.

![Project Lighthouse Dashboard](https://i.imgur.com/9a5x4rY.png)

## Core Skills Showcased
- **Full-Stack Development:** Python (Flask), React (JavaScript)
- **Data Pipeline (ETL):** Python (Pandas), SQL, Data Validation (`pandera`)
- **Database Architecture:** SQLite with a normalized, relational schema.
- **Data Science & AI:** Scikit-learn (`RandomForestClassifier`), Model Explainability (`shap`)
- **Frontend Development:** React, Chart.js, Bootstrap, Axios

---

## Project Architecture

The project is composed of a Python backend (data processing and API) and a React frontend.

### Backend Workflow

1.  **`1_generate_data.py`**: Simulates a realistic dataset of CapEx projects using `pandas` and `Faker` and saves it as `mock_capex_data.csv`.

2.  **`2_build_database.py`**: An advanced ETL script that:
    *   **Validates** the raw data against a formal schema using `pandera`.
    *   **Transforms** the data, cleaning it and engineering new features (e.g., `ScheduleVariance_Days`).
    *   **Loads** the data into a **normalized SQLite database** (`lighthouse.db`) with three related tables: `projects`, `vendors`, and `properties`.

3.  **`3_run_prediction_model.py`**: A script that demonstrates a complete MLOps workflow:
    *   Loads and joins data from the normalized database.
    *   Trains a `RandomForestClassifier` model on completed projects to predict which ongoing projects are "At Risk".
    *   Uses the **SHAP** library to provide **model explainability**, determining the `PrimaryRiskFactor` for each prediction.
    *   Updates the `projects` table with the `RiskScore`, `PredictedRisk`, and `PrimaryRiskFactor`.

4.  **`4_app.py`**: A `Flask` API that serves the enriched data from the database. It features a `/api/projects` endpoint with dynamic filtering capabilities and is CORS-enabled to communicate with the frontend.

### Frontend Architecture

The `frontend/` directory contains a **React** application that provides an interactive dashboard for visualizing the project data.

- **Live API Connection:** Fetches data dynamically from the Flask backend using `axios`.
- **Interactive Dashboard:** Built with `Chart.js`, it displays:
    - Key Performance Indicators (KPIs) for a high-level overview.
    - A doughnut chart of project risk distribution.
    - A bar chart showing the number of projects per city.
- **Filterable & Sortable Table:** Allows users to filter projects by status, risk, or city, and sort by budget or risk score.
- **Detailed Modal View:** Users can click on any project in the table to see a detailed modal pop-up with all relevant information.

---

## How to Run This Project

Follow these steps to set up and run the full application.

### Step 1: Set Up the Backend

First, ensure you have Python 3 installed. Then, set up a virtual environment and install the required packages.

```bash
# Navigate to the root directory

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the required Python libraries
pip install -r requirements.txt
```

### Step 2: Run the Data Pipeline

Run the following scripts in order to generate the data and populate the database with risk predictions.

```bash
# 1. Generate mock data
python 1_generate_data.py

# 2. Build the database
python 2_build_database.py

# 3. Run the predictive model and explainability analysis
python 3_run_prediction_model.py
```

### Step 3: Set Up the Frontend

In a separate terminal, navigate to the `frontend` directory and install the Node.js dependencies.

```bash
cd frontend
npm install
```

### Step 4: Run the Application

You will need two terminals running concurrently.

- **In your first terminal (root directory), start the Flask API server:**
  ```bash
  flask --app 4_app run
  ```
  *The backend API will be running at `http://127.0.0.1:5000`.*

- **In your second terminal (inside the `frontend` directory), start the React App:**
  ```bash
  npm start
  ```
  *A browser window should automatically open to `http://localhost:3000` with the live application.*

You can now interact with the full-stack application.