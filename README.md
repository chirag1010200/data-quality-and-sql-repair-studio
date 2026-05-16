# Data Quality & SQL Repair Studio

A modular data quality profiling and SQL-based repair system built using Python, Streamlit, Pandas, and DuckDB.

The project detects common data quality issues in messy datasets, generates SQL repair logic automatically, executes the generated SQL using DuckDB, and displays the cleaned dataset through an interactive web application.

---

# Features

## Data Profiling & Validation

The system detects:

- Schema mismatches
- Type drift
- Null violations
- Duplicate keys
- Out-of-domain values
- Email format inconsistencies
- Phone format inconsistencies
- Date format inconsistencies

---

## SQL-Based Data Repair

Automatically generates runnable DuckDB SQL for:

- Type normalization
- Boolean normalization
- Email cleaning
- Phone normalization
- Country standardization
- City normalization
- Segment normalization
- Null handling
- Invalid date handling
- Duplicate removal

The generated SQL is executed directly against the raw dataset using DuckDB to produce the cleaned dataset.

---

## Interactive Web App

Built using Streamlit.

The UI includes:

- Raw dataset view
- Reference dataset view
- Detailed issue reports
- Generated SQL view
- Cleaned dataset view
- Raw vs cleaned comparison
- Side-by-side issue summary

---

# Tech Stack

- Python
- Streamlit
- Pandas
- DuckDB

---

# Setup Instructions

## Clone Repository
-  git clone <repository-url>
-  cd data-quality-studio

## Create Virtual Environment
- python -m venv venv

## Activate Virtual Environment

## Install Dependencies
- pip install -r requirements.txt

## Running the application
- The project can be started using a single command: ./run.sh
- This launches a Streamlit application

---

# How the Application Works

## Step 1 — Upload Datasets

The user uploads:

- A raw dataset containing messy/inconsistent data
- A reference dataset containing clean canonical data and expected formats

The application loads both datasets into Pandas DataFrames.


## Step 2 — Profiling Engine Runs

The profiling engine automatically discovers and executes all issue checker modules inside:
apps/profiler/

## Step 3 — SQL Repair Generation

Based on the detected issues, the system dynamically generates repair SQL using DuckDB-compatible syntax.

The generated SQL performs operations such as:

- Type normalization
- Email validation and cleanup
- Phone normalization
- Country standardization
- City normalization
- Segment normalization
- Null handling
- Invalid date handling
- Duplicate removal


## Step 4 — DuckDB SQL Execution

The generated SQL is executed directly on the raw dataset using DuckDB.

The pipeline is:

Raw CSV
→ Profiling
→ Issue Detection
→ SQL Generation
→ DuckDB Execution
→ Cleaned Dataset


## Step 5 — Interactive Reporting UI

The Streamlit web application displays:

- Raw dataset
- Reference dataset
- Detailed issue reports
- Generated SQL
- Cleaned dataset
- Raw vs cleaned comparison
- Side-by-side issue summary

This allows users to inspect:
- detected problems
- generated fixes
- final repaired data

---

# Dynamic Checker Architecture

One of the core design goals of this project is extensibility.

The profiling engine automatically discovers all checker files ending with:

`_checker.py`

Each checker exposes:

```python
def run_check(raw_df, ref_df):
```

This means adding a new issue type does NOT require modifying the profiling engine.

---

# Adding a New Issue Type

To add a new issue type:

## 1. Create a New Checker File

Example:

`apps/profiler/range_checker.py`

---

## 2. Implement `run_check()`

Example:

```python
def run_check(raw_df, ref_df):

    issues = []

    if "age" in raw_df.columns:

        invalid = raw_df[
            (raw_df["age"] < 0) |
            (raw_df["age"] > 120)
        ]

        if not invalid.empty:

            issues.append({
                "column": "age",
                "issue_type": "invalid_age_range",
                "invalid_values":
                    invalid["age"].tolist()
            })

    return issues
```

---

## 3. Done

The engine automatically discovers and runs the new checker.

No changes to:

- `engine.py`
- `ui.py`
- imports

are required.

---

# Example Data Quality Repairs

## Email Repair

Invalid emails become:

`INVALID_EMAIL`

---

## Phone Repair

Phones are normalized to:

`+91-XXXXXXXXXX`

Invalid phones become:

`INVALID_PHONE`

---

## Country Normalization

Examples:

| Raw Value | Cleaned |
|---|---|
| india | IN |
| U.K. | UK |
| United States | US |

---

## Duplicate Removal

Duplicate customer IDs are removed using:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
)
```

---

# Acceptance Criteria Coverage

This project satisfies:

- Runnable from clean clone using single command
- SQL executes successfully in DuckDB
- Dynamic issue checker extensibility
- Separation of schema-level and content-level issues
- Modular repository structure

---

# Future Improvements

Possible future enhancements:

- Audit columns
- Repair confidence scoring
- ML-based anomaly detection
- Downloadable cleaned CSV export

---