# Project Lighthouse: Capital Intelligence & Forecasting Hub

A full-stack web application that provides real-time analytics and predictive insights for a real estate capital expenditure portfolio.

## Live Demo

[Link to your deployed Vercel app]

## Screenshots

![Project Lighthouse Dashboard](https://i.imgur.com/9a5x4rY.png)

*Replace with your own screenshots or GIFs.*

## About The Project

Project Lighthouse is a comprehensive, full-stack demonstration of a data analytics and intelligence solution for a fictional real estate investment firm. It showcases an end-to-end workflow, from data simulation and ETL to predictive modeling, model explainability, and a dynamic frontend dashboard.

The project is composed of a Python backend (data processing and API) and a React frontend.

### Backend Workflow

1.  **`1_generate_data.py`**: Simulates a realistic dataset of CapEx projects using `pandas` and `Faker`.
2.  **`2_build_database.py`**: An advanced ETL script that validates, transforms, and loads the data into a normalized SQLite database.
3.  **`3_run_prediction_model.py`**: A script that trains a `RandomForestClassifier` model to predict which ongoing projects are "At Risk" and uses the **SHAP** library to provide model explainability.
4.  **`4_app.py`**: A `Flask` API that serves the enriched data from the database.

### Frontend Architecture

The `frontend/` directory contains a **React** application that provides an interactive dashboard for visualizing the project data, featuring a live API connection, interactive charts, and a filterable table.

## Tech Stack

*   **Frontend:** React, Chart.js, Bootstrap, Axios
*   **Backend:** Python, Flask
*   **Database:** SQLite
*   **Data Science & AI:** Pandas, Scikit-learn, SHAP, Pandera

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3
*   Node.js and npm

### Installation

1.  **Backend Setup**
    ```bash
    # Clone the repo
    git clone https://github.com/your_username/your_project.git
    cd your_project

    # Create a virtual environment and activate it
    python3 -m venv venv
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt

    # Run the data pipeline
    python 1_generate_data.py
    python 2_build_database.py
    python 3_run_prediction_model.py

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
