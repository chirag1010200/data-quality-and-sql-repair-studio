def infer_schema(reference_df):
    schema = {}

    for col in reference_df.columns:
        schema[col] = str(reference_df[col].dtype)

    return schema