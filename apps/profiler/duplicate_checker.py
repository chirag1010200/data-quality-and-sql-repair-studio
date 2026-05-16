def run_check(raw_df, ref_df):

    key = "customer_id"

    duplicates = raw_df[
        raw_df.duplicated(subset=[key])
    ]

    return duplicates.to_dict(orient="records")