def generate_sql(results, raw_df):

    transformed_columns = {}

    # TYPE FIXES
    for issue in results.get("type_issues", []):

        column = issue["column"]

        expected = issue["expected"]

        if "int" in expected:

            transformed_columns[column] = (
                f"CAST({column} AS INTEGER) AS {column}"
            )

        elif "bool" in expected:

            transformed_columns[column] = f"""
            CASE

                WHEN LOWER(TRIM({column}))
                    IN ('true', '1', 'yes', 'y')
                THEN TRUE

                WHEN LOWER(TRIM({column}))
                    IN ('false', '0', 'no', 'n')
                THEN FALSE

                ELSE NULL

            END AS {column}
            """

    # EMAIL CLEANING
    if "email" in raw_df.columns:

        transformed_columns["email"] = """
        CASE

            WHEN REGEXP_MATCHES(
                LOWER(TRIM(email)),
                '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
            )

            THEN LOWER(TRIM(email))

            ELSE 'INVALID_EMAIL'

        END AS email
        """

    # FULL NAME CLEANING
    if "full_name" in raw_df.columns:

        transformed_columns["full_name"] = """
        CASE

            WHEN full_name IS NULL
                OR TRIM(full_name) = ''
            THEN 'UNKNOWN'

            ELSE

                UPPER(
                    SUBSTR(
                        SPLIT_PART(
                            REGEXP_REPLACE(
                                LOWER(TRIM(full_name)),
                                '\\s+',
                                ' ',
                                'g'
                            ),
                            ' ',
                            1
                        ),
                        1,
                        1
                    )
                ) ||

                LOWER(
                    SUBSTR(
                        SPLIT_PART(
                            REGEXP_REPLACE(
                                LOWER(TRIM(full_name)),
                                '\\s+',
                                ' ',
                                'g'
                            ),
                            ' ',
                            1
                        ),
                        2
                    )
                )

                ||

                CASE

                    WHEN STRPOS(
                        REGEXP_REPLACE(
                            LOWER(TRIM(full_name)),
                            '\\s+',
                            ' ',
                            'g'
                        ),
                        ' '
                    ) > 0

                    THEN

                        ' ' ||

                        UPPER(
                            SUBSTR(
                                SPLIT_PART(
                                    REGEXP_REPLACE(
                                        LOWER(TRIM(full_name)),
                                        '\\s+',
                                        ' ',
                                        'g'
                                    ),
                                    ' ',
                                    2
                                ),
                                1,
                                1
                            )
                        ) ||

                        LOWER(
                            SUBSTR(
                                SPLIT_PART(
                                    REGEXP_REPLACE(
                                        LOWER(TRIM(full_name)),
                                        '\\s+',
                                        ' ',
                                        'g'
                                    ),
                                    ' ',
                                    2
                                ),
                                2
                            )
                        )

                    ELSE ''

                END

        END AS full_name
        """

    # PHONE CLEANING
    if "phone" in raw_df.columns:

        transformed_columns["phone"] = """
        CASE

            WHEN LENGTH(
                REGEXP_REPLACE(phone, '[^0-9]', '', 'g')
            ) IN (10, 12)

            THEN '+91-' ||
                RIGHT(
                    REGEXP_REPLACE(phone, '[^0-9]', '', 'g'),
                    10
                )

            ELSE 'INVALID_PHONE'

        END AS phone
        """

    # DATE CLEANING
    if "signup_date" in raw_df.columns:

        transformed_columns["signup_date"] = """
        CASE

            WHEN TRY_CAST(signup_date AS DATE)
                IS NOT NULL

            THEN CAST(
                TRY_CAST(signup_date AS DATE)
                AS VARCHAR
            )

            ELSE 'INVALID_DATE'

        END AS signup_date
        """
        

    # COUNTRY CLEANING
    if "country" in raw_df.columns:

        transformed_columns["country"] = """
        CASE

            WHEN LOWER(TRIM(country))
                IN ('india', 'in')
            THEN 'IN'

            WHEN LOWER(TRIM(country))
                IN ('united states', 'usa', 'us')
            THEN 'US'

            WHEN LOWER(TRIM(country))
                IN ('u.k.', 'uk')
            THEN 'UK'

            WHEN LOWER(TRIM(country))
                = 'ae'
            THEN 'AE'

            WHEN LOWER(TRIM(country))
                = 'sg'
            THEN 'SG'

            ELSE NULL

        END AS country
        """

        # CITY CLEANING
    if "city" in raw_df.columns:

        transformed_columns["city"] = """
        CASE

            WHEN city IS NULL
                OR TRIM(city) = ''
            THEN 'UNKNOWN'

            ELSE

                UPPER(
                    SUBSTR(
                        LOWER(TRIM(city)),
                        1,
                        1
                    )
                ) ||

                LOWER(
                    SUBSTR(
                        LOWER(TRIM(city)),
                        2
                    )
                )

        END AS city
        """

    # SEGMENT CLEANING
    if "segment" in raw_df.columns:

        transformed_columns["segment"] = """
        CASE

            WHEN segment IS NULL
                OR TRIM(segment) = ''
            THEN 'UNKNOWN'

            WHEN LOWER(TRIM(segment))
                IN ('premium', 'primium')
            THEN 'premium'

            WHEN LOWER(TRIM(segment))
                IN ('enterprise', 'enterprize')
            THEN 'enterprise'

            WHEN LOWER(TRIM(segment))
                = 'retail'
            THEN 'retail'

            ELSE 'INVALID_SEGMENT'

        END AS segment
        """

    # NULL FIXES
    for issue in results.get("null_issues", []):

        column = issue["column"]

        if column not in transformed_columns:

            transformed_columns[column] = (
                f"COALESCE({column}, 'UNKNOWN') AS {column}"
            )

    # REMOVE EXTRA COLUMNS
    extra_columns = results["schema_issues"]["extra_columns"]

    # BUILD FINAL SELECT
    final_columns = []

    for col in raw_df.columns:

        if col in extra_columns:
            continue

        if col in transformed_columns:

            final_columns.append(
                transformed_columns[col]
            )

        else:

            final_columns.append(col)

    select_clause = ",\n".join(final_columns)

    final_query = f"""
    WITH cleaned AS (

        SELECT
            {select_clause}

        FROM raw_data

    ),

    deduplicated AS (

        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY customer_id
                   ORDER BY customer_id
               ) AS rn

        FROM cleaned

    )

    SELECT *
    EXCLUDE(rn)

    FROM deduplicated

    WHERE rn = 1;
    """

    return final_query