import os
import sqlite3
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration & Initialization ---
DB_FILE_PATH = 'lighthouse.db'

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: Gemini API key is not configured. Please create a .env file and add GEMINI_API_KEY='YOUR_API_KEY'")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_db_schema(db_path):
    """Reads the CREATE TABLE statements from the SQLite database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
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

### Rules:
1. You must only use the tables and columns defined in the schema above. Pay close attention to the table names (`projects`, `properties`, `vendors`) and their relationships.
2. The generated SQL must be for the SQLite dialect.
3. Your output must be **only** a single, valid SQL query and nothing else. Do not include explanations, comments, or markdown formatting like ` ```sql `.

### User Question:
"{question}"

### SQL Query:
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
    """Main orchestrator for the Text-to-SQL chatbot."""
    print(f"Received question: {question}")
    
    # 1. Get Schema
    schema = get_db_schema(DB_FILE_PATH)
    
    # 2. Generate SQL
    sql_query = generate_sql_from_question(schema, question)
    if not sql_query:
        return "Sorry, I couldn't generate an SQL query for your question."
    print(f"Generated SQL: {sql_query}")

    # 3. Validate SQL (Security Check)
    if not re.match(r"^\s*SELECT", sql_query, re.IGNORECASE):
        print(f"Validation failed: Non-SELECT query generated: {sql_query}")
        return "I can only process read-only (SELECT) queries."
    
    # 4. Execute SQL
    results = run_sql_query(DB_FILE_PATH, sql_query)
    print(f"Query results: {results}")

    # 5. Generate Final Answer
    final_answer = generate_answer_from_result(question, sql_query, results)
    print(f"Final answer: {final_answer}")
    
    return final_answer
