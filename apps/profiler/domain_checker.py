CATEGORICAL_COLUMNS = [
    "country",
    "segment",
    "is_active"
]


def run_check(raw_df, ref_df): #check_domain was the old name

    issues = []

    for col in CATEGORICAL_COLUMNS:

        if col in raw_df.columns and col in ref_df.columns:

            # NORMALIZED VALUES FOR INTERNAL COMPARISON
            valid_values = set(
                ref_df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.lower()
                .unique()
            )

            # ORIGINAL/CANONICAL VALUES FOR UI DISPLAY
            display_values = sorted(
                ref_df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            # NORMALIZE RAW VALUES BEFORE VALIDATION
            normalized_raw = (
                raw_df[col]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            # FIND INVALID ROWS
            invalid_rows = raw_df[
                ~normalized_raw.isin(valid_values)
            ]

            if not invalid_rows.empty:

                issues.append({

                    "column": col,

                    "invalid_values":
                        [str(v) for v in invalid_rows[col]
                        .unique()
                        .tolist()],

                    "expected_values":
                        display_values
                })

    return issues