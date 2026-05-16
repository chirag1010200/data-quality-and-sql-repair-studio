import duckdb
# from apps.utils.loader import load_csv

# from apps.profiler.engine import run_all_checks

# from apps.sql_generator.generator import generate_sql
from utils.loader import load_csv

from profiler.engine import run_all_checks

from sql_generator.generator import generate_sql


# LOAD DATASETS
raw_df = load_csv("../data/raw/customers_raw.csv")

ref_df = load_csv("../data/reference/customers_reference.csv")


# RUN PROFILING CHECKS
results = run_all_checks(raw_df, ref_df)


# GENERATE SQL
sql_query = generate_sql(results, raw_df)


# PRINT ISSUES
print("\n DETECTED ISSUES:\n")

print(results)


# PRINT GENERATED SQL
print("\n GENERATED SQL:\n")

print(sql_query)

# EXECUTE GENERATED SQL

con = duckdb.connect()

con.register("raw_data", raw_df)

cleaned_df = con.execute(sql_query).df()

print("\n CLEANED DATA:\n")

print(cleaned_df.head())