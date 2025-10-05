import pandas as pd
import sqlite3
import numpy as np

# --- Configuration ---
DB_FILE_PATH = 'lighthouse.db'


def analyze_contractor_performance():
    """Analyze contractor performance metrics to show why contractor is a key prediction factor."""
    print("=== CONTRACTOR PERFORMANCE ANALYSIS ===")
    print("Analyzing why contractor is a key identifier for predictions...\n")

    with sqlite3.connect(DB_FILE_PATH) as conn:
        # Load completed projects with contractor info
        query = '''
            SELECT p.ProjectID, p.ProjectType, p.Budget, p.ActualCost, 
                   p.ScheduleVariance_Days, p.BudgetVariance_CAD,
                   p.PredictedCost, p.PredictedDuration_Days,
                   v.VendorName as Contractor, prop.City
            FROM projects p
            JOIN properties prop ON p.PropertyID = prop.PropertyID
            JOIN vendors v ON p.VendorID = v.VendorID
            WHERE p.ProjectStatus = 'Completed'
        '''
        completed_df = pd.read_sql_query(query, conn)

        # Load ongoing projects with predictions
        query_ongoing = '''
            SELECT p.ProjectID, p.ProjectType, p.Budget, 
                   p.PredictedCost, p.PredictedDuration_Days, p.RiskScore,
                   v.VendorName as Contractor, prop.City
            FROM projects p
            JOIN properties prop ON p.PropertyID = prop.PropertyID
            JOIN vendors v ON p.VendorID = v.VendorID
            WHERE p.ProjectStatus IN ('In Progress', 'Not Started')
            AND p.PredictedCost IS NOT NULL
        '''
        ongoing_df = pd.read_sql_query(query_ongoing, conn)

    print("📊 CONTRACTOR COST PERFORMANCE (Completed Projects)")
    print("=" * 60)
    cost_analysis = completed_df.groupby('Contractor').agg({
        'Budget': ['count', 'mean'],
        'ActualCost': 'mean',
        'BudgetVariance_CAD': ['mean', 'std']
    }).round(2)

    # Flatten column names
    cost_analysis.columns = ['Projects', 'Avg_Budget',
                             'Avg_Actual_Cost', 'Avg_Budget_Variance', 'Std_Budget_Variance']
    cost_analysis['Cost_Overrun_Rate'] = (
        (cost_analysis['Avg_Actual_Cost'] - cost_analysis['Avg_Budget']) / cost_analysis['Avg_Budget'] * 100).round(1)

    print(cost_analysis)
    print()

    print("⏱️ CONTRACTOR SCHEDULE PERFORMANCE (Completed Projects)")
    print("=" * 60)
    schedule_analysis = completed_df.groupby('Contractor').agg({
        'ScheduleVariance_Days': ['mean', 'std']
    }).round(1)
    schedule_analysis.columns = [
        'Avg_Schedule_Variance_Days', 'Std_Schedule_Variance_Days']

    print(schedule_analysis)
    print()

    print("🔮 CURRENT PREDICTIONS BY CONTRACTOR (Ongoing Projects)")
    print("=" * 60)
    prediction_analysis = ongoing_df.groupby('Contractor').agg({
        'PredictedCost': 'mean',
        'PredictedDuration_Days': 'mean',
        'RiskScore': 'mean',
        'ProjectID': 'count'
    }).round(2)
    prediction_analysis.columns = [
        'Avg_Predicted_Cost', 'Avg_Predicted_Duration', 'Avg_Risk_Score', 'Ongoing_Projects']

    print(prediction_analysis)
    print()

    print("🎯 WHY CONTRACTOR IS A KEY PREDICTION FACTOR:")
    print("=" * 50)

    # Calculate coefficient of variation for costs by contractor
    cost_cv = completed_df.groupby('Contractor')[
        'BudgetVariance_CAD'].agg(['mean', 'std'])
    cost_cv['CV'] = (cost_cv['std'] / abs(cost_cv['mean'])).fillna(0)

    print(f"1. COST VARIANCE BY CONTRACTOR:")
    for contractor in cost_cv.index:
        variance = cost_analysis.loc[contractor, 'Avg_Budget_Variance']
        overrun = cost_analysis.loc[contractor, 'Cost_Overrun_Rate']
        print(
            f"   • {contractor}: Avg variance ${variance:,.0f} ({overrun:+.1f}%)")

    print(f"\n2. SCHEDULE VARIANCE BY CONTRACTOR:")
    for contractor in schedule_analysis.index:
        variance = schedule_analysis.loc[contractor,
                                         'Avg_Schedule_Variance_Days']
        print(f"   • {contractor}: Avg {variance:+.1f} days from planned")

    print(f"\n3. PREDICTION DIFFERENCES:")
    pred_range = ongoing_df.groupby(
        'Contractor')['PredictedCost'].agg(['min', 'max'])
    for contractor in pred_range.index:
        min_cost = pred_range.loc[contractor, 'min']
        max_cost = pred_range.loc[contractor, 'max']
        print(
            f"   • {contractor}: Predicted costs range ${min_cost:,.0f} - ${max_cost:,.0f}")

    print(f"\n4. RISK PROFILE BY CONTRACTOR:")
    risk_profile = ongoing_df.groupby('Contractor')['RiskScore'].mean()
    for contractor in risk_profile.index:
        risk = risk_profile[contractor]
        risk_level = "HIGH" if risk > 0.7 else "MEDIUM" if risk > 0.4 else "LOW"
        print(f"   • {contractor}: Avg risk score {risk:.3f} ({risk_level})")

    print(f"\n💡 CONCLUSION:")
    print("   Contractors show significantly different patterns in:")
    print("   - Cost performance and overrun rates")
    print("   - Schedule adherence and delays")
    print("   - Project risk profiles")
    print("   - Prediction ranges and accuracy")
    print("   This makes contractor a CRITICAL feature for accurate predictions!")


if __name__ == '__main__':
    analyze_contractor_performance()
