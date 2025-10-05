import os
import sqlite3
import re
import json
import base64
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("Warning: matplotlib not available. Chart generation disabled.")

# Load environment variables from .env file
load_dotenv()

# --- Configuration & Initialization ---
DB_FILE_PATH = 'lighthouse.db'

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: Gemini API key is not configured. Please create a .env file and add GEMINI_API_KEY='YOUR_API_KEY'")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


def is_chart_request(question):
    """Detect if the user is asking for a chart or visualization."""
    chart_keywords = [
        'chart', 'graph', 'plot', 'visualize', 'bar chart', 'pie chart',
        'line chart', 'show me a chart', 'create a chart', 'display', 'visual'
    ]
    return any(keyword in question.lower() for keyword in chart_keywords)


def create_chart_from_data(data, title, chart_type='bar'):
    """Create a chart from SQL query results and return as base64."""
    if not CHARTS_AVAILABLE:
        return None

    try:
        plt.figure(figsize=(12, 8))

        # Extract data for chart
        if isinstance(data, list) and len(data) > 0:
            # Get the first row to determine structure
            first_row = data[0]

            if len(first_row) >= 3:  # Vendor, Budget, Actual pattern
                vendors = [row[list(row.keys())[0]] for row in data]
                budgets = [float(row[list(row.keys())[1]] or 0)
                           for row in data]
                actuals = [float(row[list(row.keys())[2]] or 0)
                           for row in data]

                x_pos = range(len(vendors))
                width = 0.35

                plt.bar([p - width/2 for p in x_pos], budgets, width,
                        label='Budget', alpha=0.8, color='#3498db')
                plt.bar([p + width/2 for p in x_pos], actuals, width,
                        label='Actual Cost', alpha=0.8, color='#e74c3c')

                plt.xlabel('Vendor')
                plt.ylabel('Amount ($)')
                plt.title(title)
                plt.xticks(x_pos, vendors, rotation=45, ha='right')
                plt.legend()

                # Format y-axis as currency
                ax = plt.gca()
                ax.yaxis.set_major_formatter(
                    plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

            elif len(first_row) == 2:  # Simple key-value pairs
                keys = [row[list(row.keys())[0]] for row in data]
                values = [float(row[list(row.keys())[1]] or 0) for row in data]

                if chart_type == 'pie':
                    plt.pie(values, labels=keys, autopct='%1.1f%%')
                else:
                    plt.bar(keys, values, color='#3498db', alpha=0.8)
                    plt.xticks(rotation=45, ha='right')

                plt.title(title)

        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150,
                    bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        chart_b64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return chart_b64

    except Exception as e:
        print(f"Error creating chart: {e}")
        plt.close()
        return None


def get_db_schema(db_path):
    """Reads the CREATE TABLE statements from the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table';")
        schema_str = "\n".join([row[1] for row in cursor.fetchall()])
    return schema_str


def generate_sql_from_question(schema, question):
    """Uses the LLM to generate an SQL query from a natural language question."""
    prompt = f"""
You are an expert SQLite data analyst. Your task is to convert a user's natural language question into a valid SQLite query based on the database schema provided below.

### Database Schema:
```sql
{schema}
```

### Important Rules:
1. You must ONLY generate SELECT queries - no INSERT, UPDATE, DELETE, or CREATE statements
2. Use only the tables and columns defined in the schema: `projects`, `properties`, `vendors`
3. Always start your response with "SELECT" 
4. For questions about:
   - "How many projects" → use COUNT(*)
   - "High-risk projects" → use WHERE PredictedRisk = 'High'
   - "Average budget" → use AVG(Budget)
   - "Projects in [city]" → JOIN with properties table and filter by City
   - "Completed projects" → use WHERE ProjectStatus = 'Completed'
5. Join tables when needed: projects → properties (PropertyID), projects → vendors (VendorID)

### User Question:
"{question}"

### SQL Query (start with SELECT):
"""
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        # Clean up potential markdown formatting
        sql_query = re.sub(r"^```sql\n|```$", "", sql_query).strip()
        return sql_query
    except Exception as e:
        print(f"Error calling Gemini API for SQL generation: {e}")
        return None


def run_sql_query(db_path, query):
    """Executes a SELECT query and returns the results."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except sqlite3.Error as e:
        print(f"Database query failed: {e}")
        return {"error": str(e)}


def generate_answer_from_result(question, sql_query, results):
    """Uses the LLM to generate a human-readable answer from the query results."""
    prompt = f"""
You are a helpful assistant. Based on the user's original question and the data retrieved from the database, provide a concise, human-readable answer.

### Original Question:
"{question}"

### Executed SQL Query:
```sql
{sql_query}
```

### Data:
{results}

### Answer:
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API for answer generation: {e}")
        return "Sorry, I encountered an error while formulating the answer."


def ask_chatbot(question):
    """Main orchestrator for the Text-to-SQL chatbot with chart generation."""
    print(f"Received question: {question}")

    # Check if this is a chart request
    is_chart = is_chart_request(question)

    # 1. Get Schema
    schema = get_db_schema(DB_FILE_PATH)

    # 2. Generate SQL (enhance for chart requests)
    if is_chart:
        # Enhance the question for better SQL generation for charts
        enhanced_question = question
        if 'vendor' in question.lower() and 'budget' in question.lower():
            enhanced_question = "Show vendor name, total budget, and total actual cost for completed projects grouped by vendor"
    else:
        enhanced_question = question

    sql_query = generate_sql_from_question(schema, enhanced_question)
    if not sql_query:
        return {"answer": "Sorry, I couldn't generate an SQL query for your question.", "type": "text"}
    print(f"Generated SQL: {sql_query}")

    # 3. Add fallback for chart requests
    if is_chart and 'vendor' in question.lower() and ('budget' in question.lower() or 'actual' in question.lower()):
        sql_query = "SELECT v.VendorName, SUM(p.Budget) as Total_Budget, SUM(p.ActualCost) as Total_Actual FROM projects p JOIN vendors v ON p.VendorID = v.VendorID WHERE p.ProjectStatus = 'Completed' GROUP BY v.VendorName"
        print(f"Using chart-specific SQL: {sql_query}")

    # 4. Validate SQL (Security Check)
    if not sql_query or not re.match(r"^\s*SELECT", sql_query, re.IGNORECASE):
        print(f"Validation failed: Invalid query generated: {sql_query}")
        # Try a simpler fallback approach for common questions
        if any(word in question.lower() for word in ['how many', 'count', 'total projects']):
            sql_query = "SELECT COUNT(*) as project_count FROM projects"
        elif 'high-risk' in question.lower() or 'high risk' in question.lower():
            sql_query = "SELECT COUNT(*) as high_risk_count FROM projects WHERE PredictedRisk = 'High'"
        elif 'average budget' in question.lower():
            if 'toronto' in question.lower():
                sql_query = "SELECT AVG(p.Budget) as avg_budget FROM projects p JOIN properties pr ON p.PropertyID = pr.PropertyID WHERE pr.City = 'Toronto'"
            else:
                sql_query = "SELECT AVG(Budget) as avg_budget FROM projects"
        elif 'completed' in question.lower() and ('budget' in question.lower() or 'cost' in question.lower()):
            sql_query = "SELECT SUM(Budget) as total_budget, SUM(ActualCost_CAD) as total_actual FROM projects WHERE ProjectStatus = 'Completed'"
        else:
            return {"answer": "I couldn't understand your question. Try asking about project counts, budgets, or risk levels.", "type": "text"}

        print(f"Using fallback SQL: {sql_query}")

    # Validate the fallback query
    if not re.match(r"^\s*SELECT", sql_query, re.IGNORECASE):
        return {"answer": "I can only process read-only (SELECT) queries.", "type": "text"}

    # 5. Execute SQL
    results = run_sql_query(DB_FILE_PATH, sql_query)
    print(f"Query results: {results}")

    # 6. Handle chart generation
    if is_chart and results and not isinstance(results, dict):
        chart_b64 = create_chart_from_data(
            results, f"Chart: {question}", 'bar')
        if chart_b64:
            text_answer = generate_answer_from_result(
                question, sql_query, results)
            return {
                "type": "chart",
                "answer": text_answer,
                "chart": chart_b64,
                "sql_query": sql_query,
                "results": results
            }

    # 7. Generate text answer (fallback or non-chart requests)
    final_answer = generate_answer_from_result(question, sql_query, results)
    print(f"Final answer: {final_answer}")

    return {"answer": final_answer, "type": "text"}
