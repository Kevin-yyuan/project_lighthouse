
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# --- Configuration ---
NUM_ROWS = 200
CITIES = ["Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa", "Halifax"]
PROJECT_TYPES = ["Suite Renovation", "Lobby Upgrade", "HVAC Replacement", "Roof Repair", "Window Replacement", "Parking Garage Repair"]
PROJECT_STATUSES = ["Completed", "In Progress", "Not Started"]
VENDORS = ["Apex Construction", "Stellar Renovations", "Keystone Builders", "Summit Contractors", "Precision Mechanical"]
ESG_INITIATIVES = ["LED Lighting Upgrade", "High-Efficiency HVAC", "Water Conservation Fixtures", "Solar Panel Installation", "Green Roof"]

# --- Data Generation ---
data = []
for i in range(1, NUM_ROWS + 1):
    project_id = f"CAP-{i:03d}"
    property_name = fake.company() + " Heights"
    city = random.choice(CITIES)
    project_type = random.choice(PROJECT_TYPES)
    project_status = random.choice(PROJECT_STATUSES)
    
    start_date = fake.date_between(start_date=datetime(2022, 1, 1), end_date=datetime(2024, 12, 31))
    planned_end_date = start_date + timedelta(days=random.randint(60, 365))
    
    budget = random.randint(50000, 5000000)
    vendor = random.choice(VENDORS)

    # Initialize fields that depend on status
    actual_end_date = None
    actual_cost = None
    pre_reno_rent = None
    post_reno_rent = None

    # --- Logic for "Completed" projects ---
    if project_status == "Completed":
        # Simulate schedule variance
        schedule_variance_days = random.randint(-15, 90)
        # Apex Construction is more likely to be late
        if vendor == "Apex Construction":
            schedule_variance_days = random.randint(30, 120)
        actual_end_date = planned_end_date + timedelta(days=schedule_variance_days)

        # Simulate cost variance
        cost_variance_multiplier = random.uniform(-0.05, 0.20)
        # Apex Construction is more likely to be over budget
        if vendor == "Apex Construction":
            cost_variance_multiplier = random.uniform(0.10, 0.25)
        actual_cost = budget * (1 + cost_variance_multiplier)

    # --- Logic for "Suite Renovation" projects ---
    if project_type == "Suite Renovation":
        pre_reno_rent = random.randint(1800, 2500)
        if project_status == "Completed":
            rent_multiplier = random.uniform(1.15, 1.30)
            post_reno_rent = pre_reno_rent * rent_multiplier

    # --- Logic for ESG Initiatives (25% chance) ---
    esg_initiative = random.choice(ESG_INITIATIVES) if random.random() < 0.25 else None

    data.append([
        project_id,
        property_name,
        city,
        project_type,
        project_status,
        start_date,
        planned_end_date,
        actual_end_date,
        budget,
        actual_cost,
        vendor,
        esg_initiative,
        pre_reno_rent,
        post_reno_rent
    ])

# --- Create DataFrame ---
columns = [
    "ProjectID", "PropertyName", "City", "ProjectType", "ProjectStatus",
    "StartDate", "PlannedEndDate", "ActualEndDate", "Budget", "ActualCost",
    "Vendor", "ESG_Initiative", "PreReno_Rent", "PostReno_Rent"
]
df = pd.DataFrame(data, columns=columns)

# --- Save to CSV ---
output_path = "mock_capex_data.csv"
df.to_csv(output_path, index=False, date_format='%Y-%m-%d')

print(f"Successfully generated {NUM_ROWS} rows of mock data and saved to '{output_path}'.")
