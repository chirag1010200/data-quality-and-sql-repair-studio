import pandas as pd


def run_check(raw_df, ref_df):

    issues = []

    # EMAIL FORMAT CHECK
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if "email" in raw_df.columns:

        invalid = raw_df[
            ~raw_df["email"]
            .astype(str)
            .str.match(email_pattern)
        ]

        if not invalid.empty:

            issues.append({
                "column": "email",
                "issue_type": "invalid_email_format",
                "invalid_values":
                invalid["email"].tolist()
            })

    # PHONE FORMAT CHECK
    phone_pattern = r'^\+91-\d{10}$'

    if "phone" in raw_df.columns:

        invalid = raw_df[
            ~raw_df["phone"]
            .astype(str)
            .str.match(phone_pattern)
        ]

        if not invalid.empty:

            issues.append({
                "column": "phone",
                "issue_type": "invalid_phone_format",
                "invalid_values":
                invalid["phone"].tolist()
            })

    # DATE FORMAT CHECK
    if "signup_date" in raw_df.columns:

        parsed = pd.to_datetime(
            raw_df["signup_date"],
            errors="coerce"
        )

        invalid = raw_df[parsed.isnull()]

        if not invalid.empty:

            issues.append({
                "column": "signup_date",
                "issue_type": "invalid_date_format",
                "invalid_values":
                invalid["signup_date"].tolist()
            })

    return issues