import pandas as pd
import sqlite3
import pandera as pa
from pandera.errors import SchemaError
import sys

# --- Configuration ---
CSV_FILE_PATH = 'mock_capex_data.csv'
DB_FILE_PATH = 'lighthouse.db'

# --- 1. Data Validation Schema ---
# Define the validation schema for the raw input data
raw_data_schema = pa.DataFrameSchema({
    "ProjectID": pa.Column(str, pa.Check.str_matches(r'^CAP-\d{3}$'), unique=True, required=True),
    "PropertyName": pa.Column(str, required=True),
    "City": pa.Column(str, pa.Check.isin(["Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa", "Halifax"])),
    "ProjectType": pa.Column(str, pa.Check.isin(["Suite Renovation", "Lobby Upgrade", "HVAC Replacement", "Roof Repair", "Window Replacement", "Parking Garage Repair"])),
    "ProjectStatus": pa.Column(str, pa.Check.isin(["Completed", "In Progress", "Not Started"])),
    "StartDate": pa.Column(pa.DateTime),
    "PlannedEndDate": pa.Column(pa.DateTime),
    "ActualEndDate": pa.Column(pa.DateTime, nullable=True),
    "Budget": pa.Column(int, pa.Check.greater_than_or_equal_to(50000)),
    "ActualCost": pa.Column(float, nullable=True),
    "Vendor": pa.Column(str),
    "ESG_Initiative": pa.Column(str, nullable=True),
    "PreReno_Rent": pa.Column(float, pa.Check.greater_than_or_equal_to(0), nullable=True),
    "PostReno_Rent": pa.Column(float, pa.Check.greater_than_or_equal_to(0), nullable=True),
})

# --- 2. Database Schema Definition ---
def create_database_schema(conn):
    # ... (same as before)
    print("Creating database schema...")
    cursor = conn.cursor()
    cursor.executescript('''
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS vendors;
        DROP TABLE IF EXISTS properties;
    ''')
    cursor.executescript('''
        CREATE TABLE vendors ( VendorID INTEGER PRIMARY KEY AUTOINCREMENT, VendorName TEXT NOT NULL UNIQUE );
        CREATE TABLE properties ( PropertyID INTEGER PRIMARY KEY AUTOINCREMENT, PropertyName TEXT NOT NULL, City TEXT NOT NULL, UNIQUE(PropertyName, City) );
        CREATE TABLE projects ( ProjectID TEXT PRIMARY KEY, PropertyID INTEGER, VendorID INTEGER, ProjectType TEXT, ProjectStatus TEXT, StartDate TEXT, PlannedEndDate TEXT, ActualEndDate TEXT, Budget REAL, ActualCost REAL, ESG_Initiative TEXT, PreReno_Rent REAL, PostReno_Rent REAL, ScheduleVariance_Days INTEGER, BudgetVariance_CAD REAL, ReturnOnCost_Percent REAL, RiskScore REAL, PredictedRisk TEXT, PrimaryRiskFactor TEXT, PredictedCost REAL, PredictedDuration_Days INTEGER, FOREIGN KEY (PropertyID) REFERENCES properties (PropertyID), FOREIGN KEY (VendorID) REFERENCES vendors (VendorID) );
    ''')
    print("Schema created successfully.")

# --- 3. ETL and Data Loading ---
def run_etl(conn):
    """Runs the full ETL process from CSV to normalized SQLite database."""
    print("Starting ETL process...")
    
    # --- EXTRACT ---
    print(f"Reading data from {CSV_FILE_PATH}...")
    df = pd.read_csv(CSV_FILE_PATH)

    # --- VALIDATE ---
    print("Validating raw data...")
    # First, convert date columns so pandera can validate them as datetimes
    for col in ['StartDate', 'PlannedEndDate', 'ActualEndDate']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    try:
        raw_data_schema.validate(df, lazy=True)
        print("Raw data validation successful.")
    except SchemaError as err:
        print("Raw data validation failed!")
        print(err.failure_cases)
        sys.exit(1) # Exit if data is invalid

    # --- TRANSFORM ---
    print("Transforming data and engineering features...")
    df['ScheduleVariance_Days'] = (df['ActualEndDate'] - df['PlannedEndDate']).dt.days
    df['BudgetVariance_CAD'] = df['ActualCost'] - df['Budget']
    suite_reno_mask = (df['ProjectType'] == 'Suite Renovation') & (df['ProjectStatus'] == 'Completed')
    safe_actual_cost = df.loc[suite_reno_mask, 'ActualCost'].replace(0, pd.NA)
    df['ReturnOnCost_Percent'] = pd.NA
    df.loc[suite_reno_mask, 'ReturnOnCost_Percent'] = (((df['PostReno_Rent'] - df['PreReno_Rent']) * 12) / safe_actual_cost) * 100
    
    for col in ['ActualCost', 'BudgetVariance_CAD', 'PreReno_Rent', 'PostReno_Rent']:
        df[col] = df[col].round(2)
    df['ReturnOnCost_Percent'] = pd.to_numeric(df['ReturnOnCost_Percent']).round(2)

    # --- LOAD ---
    vendors_df = pd.DataFrame(df['Vendor'].unique(), columns=['VendorName'])
    vendors_df.to_sql('vendors', conn, if_exists='append', index=False)
    print(f"Loaded {len(vendors_df)} unique vendors.")

    properties_df = df[['PropertyName', 'City']].drop_duplicates().reset_index(drop=True)
    properties_df.to_sql('properties', conn, if_exists='append', index=False)
    print(f"Loaded {len(properties_df)} unique properties.")

    vendors_map = pd.read_sql('SELECT VendorID, VendorName FROM vendors', conn).rename(columns={'VendorName': 'Vendor'})
    properties_map = pd.read_sql('SELECT PropertyID, PropertyName, City FROM properties', conn)
    
    df = df.merge(vendors_map, on='Vendor')
    df = df.merge(properties_map, on=['PropertyName', 'City'])

    projects_df = df[[
        'ProjectID', 'PropertyID', 'VendorID', 'ProjectType', 'ProjectStatus',
        'StartDate', 'PlannedEndDate', 'ActualEndDate', 'Budget', 'ActualCost',
        'ESG_Initiative', 'PreReno_Rent', 'PostReno_Rent', 'ScheduleVariance_Days',
        'BudgetVariance_CAD', 'ReturnOnCost_Percent'
    ]]
    
    for col in ['StartDate', 'PlannedEndDate', 'ActualEndDate']:
        projects_df[col] = projects_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    projects_df.to_sql('projects', conn, if_exists='append', index=False)
    print(f"Loaded {len(projects_df)} projects.")

# --- Main Execution ---
if __name__ == "__main__":
    with sqlite3.connect(DB_FILE_PATH) as conn:
        create_database_schema(conn)
        run_etl(conn)
    print("Database build process completed successfully.")