def run_check(raw_df, ref_df):

    raw_cols = set(raw_df.columns)
    ref_cols = set(ref_df.columns)

    missing = ref_cols - raw_cols
    extra = raw_cols - ref_cols

    return {
        "missing_columns": list(missing),
        "extra_columns": list(extra)
    }