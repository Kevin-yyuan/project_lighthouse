# Project Lighthouse: Capital Intelligence & Forecasting Hub

A full-stack web application that provides real-time analytics and predictive insights for a real estate capital expenditure portfolio.

## Live Demo

[Project Lighthouse](https://project-lighthouse-ruby.vercel.app/)

**Note on Performance:** The backend is deployed on Render's free tier, which spins down the service after a period of inactivity. As a result, the initial load may take up to 30 seconds while the server performs a "cold start". Subsequent requests will be much faster.

## About The Project

Project Lighthouse is a comprehensive, full-stack demonstration of a data analytics and intelligence solution for a fictional real estate investment firm. It showcases an end-to-end workflow, from data simulation and ETL to predictive modeling, model explainability, and a dynamic frontend dashboard.

The project is composed of a Python backend (data processing and API) and a React frontend.

## Data Pipeline and Backend

The backend is a sophisticated data processing pipeline that feeds a Flask API.

1.  **`1_generate_data.py`**: Simulates a realistic dataset of 200 capital expenditure projects using `pandas` and `Faker`. It generates a rich set of features including project types, budgets, timelines, and vendor assignments.

2.  **`2_build_database.py`**: An advanced ETL (Extract, Transform, Load) script that:

    - **Validates** the raw CSV data against a formal schema using `pandera` to ensure data quality and integrity.
    - **Transforms** the data by cleaning it and engineering new features such as `ScheduleVariance_Days` and `BudgetVariance_CAD`.
    - **Loads** the data into a normalized SQLite database, splitting the information into `projects`, `vendors`, and `properties` tables.

3.  **`3_enhanced_prediction_model.py`**: A script that demonstrates a complete MLOps workflow by training and applying three distinct models:

    - **Risk Prediction**: A `RandomForestClassifier` is trained on completed projects to predict which ongoing projects are "At Risk" of being late or over budget.
    - **Cost Prediction**: A `RandomForestRegressor` predicts the final `ActualCost` of ongoing projects based on their features.
    - **Duration Prediction**: A second `RandomForestRegressor` predicts the `ActualDuration_Days` for ongoing projects.
    - The script then updates the `projects` table with these predictions.

4.  **`4_app.py`**: A `Flask` API that serves the enriched data from the database. It features a `/api/projects` endpoint with dynamic filtering capabilities and is CORS-enabled to communicate with the frontend.

## Database Schema

The application uses a normalized SQLite database to ensure data integrity and prevent redundancy. The schema is composed of three tables:

- **`properties`**: Stores information about each property, including its name and city.
- **`vendors`**: Stores a list of unique vendors that can be assigned to projects.
- **`projects`**: The main table containing all project-specific information, including timelines, budgets, and the predictions from our models. It is linked to the `properties` and `vendors` tables via foreign keys.

## Tech Stack

- **Frontend:** React, Chart.js, Bootstrap, Axios
- **Backend:** Python, Flask
- **Database:** SQLite
- **Data Science & AI:** Pandas, Scikit-learn, SHAP, Pandera

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3
- Node.js and npm

### Installation

1.  **Backend Setup**

    ```bash
    # Clone the repo
    git clone https://github.com/Kevin-yyuan/project_lighthouse.git
    cd your_project

    # Create a virtual environment and activate it
    python3 -m venv venv
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt

    # Run the data pipeline and prediction models
    python 1_generate_data.py
    python 2_build_database.py
    python 3_enhanced_prediction_model.py

    # Start the backend server
    flask --app 4_app run
    ```

2.  **Frontend Setup**

    ```bash
    # In a new terminal, navigate to the frontend directory
    cd frontend

    # Install NPM packages
    npm install

    # Start the frontend development server
    npm start
    ```
