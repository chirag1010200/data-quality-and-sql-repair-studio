import os
import importlib


def run_all_checks(raw_df, ref_df):

    results = {}

    current_dir = os.path.dirname(__file__)

    for file in os.listdir(current_dir):

        print("FOUND:", file)

        # Only load checker files
        if not file.endswith("_checker.py"):
            continue

        module_name = file[:-3]

        try:

            print("LOADING:", module_name)

            module = importlib.import_module(
                f"profiler.{module_name}"
            )

            # Every checker must expose run_check()
            print("HAS run_check:", hasattr(module, "run_check"))

            if hasattr(module, "run_check"):

                issue_name = module_name.replace(
                    "_checker",
                    "_issues"
                )

                results[issue_name] = (
                    module.run_check(raw_df, ref_df)
                )

                print("SUCCESS:", issue_name)

        except Exception as e:

            print("FAILED:", module_name)
            print(e)

    return results