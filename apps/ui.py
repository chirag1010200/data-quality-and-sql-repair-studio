import streamlit as st
import pandas as pd
import duckdb

from profiler.engine import run_all_checks
from sql_generator.generator import generate_sql


# PAGE CONFIG
st.set_page_config(
    page_title="Data Quality & SQL Repair Studio",
    layout="wide"
)

st.title("Data Quality & SQL Repair Studio")


# FILE UPLOAD SECTION
st.header("Upload Datasets")

col1, col2 = st.columns(2)

with col1:
    raw_file = st.file_uploader(
        "Upload Raw Dataset",
        type=["csv"]
    )

with col2:
    reference_file = st.file_uploader(
        "Upload Reference Dataset",
        type=["csv"]
    )


if raw_file and reference_file:

    # LOAD DATA
    raw_df = pd.read_csv(raw_file)

    ref_df = pd.read_csv(reference_file)


    # RUN PROFILING
    results = run_all_checks(raw_df, ref_df)

    # st.write(results.keys())


    # FORMAT ISSUE FILTERING
    format_issues = results["format_issues"]

    email_issues = [
        issue for issue in format_issues
        if issue["issue_type"] == "invalid_email_format"
    ]

    phone_issues = [
        issue for issue in format_issues
        if issue["issue_type"] == "invalid_phone_format"
    ]

    date_issues = [
        issue for issue in format_issues
        if issue["issue_type"] == "invalid_date_format"
    ]


    # GENERATE SQL
    sql_query = generate_sql(results, raw_df)


    # EXECUTE SQL USING DUCKDB
    con = duckdb.connect()

    con.register("raw_data", raw_df)

    cleaned_df = con.execute(sql_query).df()


    # ISSUE REPORT TABLE
    issue_rows = []


    # SCHEMA ISSUES
    for col in results["schema_issues"]["extra_columns"]:

        issue_rows.append({
            "Issue Type": "Schema Mismatch",
            "Column": col,
            "Problem": "Extra column in raw dataset",
            "Suggested Fix": f"DROP COLUMN {col}"
        })


    # TYPE DRIFT ISSUES
    for issue in results["type_issues"]:

        issue_rows.append({
            "Issue Type": "Type Drift",
            "Column": issue["column"],
            "Problem":
                f'Expected {issue["expected"]}, got {issue["actual"]}',
            "Suggested Fix":
                f'CAST({issue["column"]} AS BOOLEAN)'
        })


    # NULL ISSUES
    for issue in results["null_issues"]:

        issue_rows.append({
            "Issue Type": "Null Violation",
            "Column": issue["column"],
            "Problem":
                f'{issue["null_count"]} null values',
            "Suggested Fix":
                f'COALESCE({issue["column"]}, ...)'
        })


    # EMAIL ISSUES
    for issue in email_issues:

        issue_rows.append({
            "Issue Type": "Email Format",
            "Column": issue["column"],
            "Problem":
                f'{len(issue["invalid_values"])} invalid emails',
            "Suggested Fix":
                "CASE WHEN REGEXP_MATCHES(...)"
        })


    # PHONE ISSUES
    for issue in phone_issues:

        issue_rows.append({
            "Issue Type": "Phone Format",
            "Column": issue["column"],
            "Problem":
                f'{len(issue["invalid_values"])} invalid phones',
            "Suggested Fix":
                "Normalize phone formatting"
        })


    # DATE ISSUES
    for issue in date_issues:

        issue_rows.append({
            "Issue Type": "Date Format",
            "Column": issue["column"],
            "Problem":
                f'{len(issue["invalid_values"])} invalid dates',
            "Suggested Fix":
                "TRY_CAST(signup_date AS DATE)"
        })


    issues_df = pd.DataFrame(issue_rows)


    # TABS
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Input Data",
        "Issues",
        "Generated SQL",
        "Cleaned Data",
        "Comparison",
        "Issue Report"
    ])


    # TAB 1 — RAW DATA
    with tab1:

        st.header("Raw Dataset")
        st.dataframe(raw_df)

        st.header("Reference Dataset")
        st.dataframe(ref_df)


    # TAB 2 — ISSUES
    with tab2:

        st.header("Schema-Level Issues")


        # SCHEMA
        st.subheader("Schema Mismatches")

        schema_df = pd.DataFrame([
            {
                "Missing Columns":
                    results["schema_issues"]["missing_columns"],

                "Extra Columns":
                    results["schema_issues"]["extra_columns"]
            }
        ])

        st.dataframe(schema_df)


        # TYPE DRIFT
        st.subheader("Type Drift")

        st.dataframe(
            pd.DataFrame(results["type_issues"])
        )


        # CONTENT ISSUES
        st.header("Content-Level Issues")


        # NULLS
        st.subheader("Null Violations")

        st.dataframe(
            pd.DataFrame(results["null_issues"])
        )


        # DUPLICATES
        st.subheader("Duplicate Keys")

        st.dataframe(
            pd.DataFrame(results["duplicate_issues"])
        )


        # DOMAIN ISSUES
        st.subheader("Domain Issues")

        st.dataframe(
            pd.DataFrame(results["domain_issues"])
        )


        # EMAIL FORMAT
        st.subheader("Email Format Issues")

        if email_issues:

            email_df = pd.DataFrame({
                "invalid_email":
                    email_issues[0]["invalid_values"]
            })

            st.dataframe(email_df)


        # PHONE FORMAT
        st.subheader("Phone Format Issues")

        if phone_issues:

            phone_df = pd.DataFrame({
                "invalid_phone":
                    phone_issues[0]["invalid_values"]
            })

            st.dataframe(phone_df)


        # DATE FORMAT
        st.subheader("Date Format Issues")

        if date_issues:

            date_df = pd.DataFrame({
                "invalid_date":
                    date_issues[0]["invalid_values"]
            })

            st.dataframe(date_df)


    # TAB 3 — SQL
    with tab3:

        st.header("Generated SQL")

        st.code(sql_query, language="sql")

        st.download_button(
            label="Download SQL",
            data=sql_query,
            file_name="repair.sql",
            mime="text/sql"
        )


    # TAB 4 — CLEANED DATA
    with tab4:

        st.header("Cleaned Dataset")

        st.dataframe(cleaned_df)


    # TAB 5 — COMPARISON
    with tab5:

        st.header("Raw vs Cleaned Comparison")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Raw Dataset")

            st.dataframe(raw_df)

        with col2:

            st.subheader("Cleaned Dataset")

            st.dataframe(cleaned_df)


    # TAB 6 — ISSUE REPORT
    with tab6:

        st.header("Side-by-Side Issues Report")

        st.dataframe(issues_df)