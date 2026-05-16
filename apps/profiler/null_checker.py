def run_check(raw_df, ref_df):

    issues = []

    for col in raw_df.columns:

        null_count = raw_df[col].isnull().sum()

        if null_count > 0:

            issues.append({
                "column": col,
                "null_count": int(null_count)
            })

    return issues