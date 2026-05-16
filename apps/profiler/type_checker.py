def run_check(raw_df, ref_df):

    issues = []

    for col in ref_df.columns:

        if col in raw_df.columns:

            ref_type = str(ref_df[col].dtype)
            raw_type = str(raw_df[col].dtype)

            if ref_type != raw_type:

                issues.append({
                    "column": col,
                    "expected": ref_type,
                    "actual": raw_type
                })

    return issues