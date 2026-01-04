# export_brd.py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def export_to_excel(brd_json, filename):
    """
    Exports a BRD JSON (validated against the response schema)
    into a structured Excel workbook.
    """

    logger.info("Starting BRD Excel export")

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:

        # -------------------------
        # Section 1 — Tables Needed
        # -------------------------
        logger.info("Writing Section 1 — Tables Needed")
        pd.DataFrame(
            {"Tables Needed": brd_json["Section 1 — Tables Needed"]}
        ).to_excel(writer, sheet_name="1_Tables", index=False)

        # -------------------------
        # Section 2 — Columns Needed
        # -------------------------
        logger.info("Writing Section 2 — Columns Needed")
        pd.DataFrame(
            {"Columns Needed": brd_json["Section 2 — Columns Needed"]}
        ).to_excel(writer, sheet_name="2_Columns", index=False)

        # -------------------------
        # Section 3 — Joins
        # -------------------------
        logger.info("Writing Section 3 — Joins")
        pd.DataFrame(
            brd_json["Section 3 — Joins"],
            columns=["Left Table", "Right Table", "Join Type", "Condition"]
        ).to_excel(writer, sheet_name="3_Joins", index=False)

        # -------------------------
        # Section 4 — Filters
        # -------------------------
        logger.info("Writing Section 4 — Filters")
        pd.DataFrame(
            brd_json["Section 4 — Filters"],
            columns=["Column", "Operator", "Value"]
        ).to_excel(writer, sheet_name="4_Filters", index=False)

        # -------------------------
        # Section 5 — Transformations
        # -------------------------
        logger.info("Writing Section 5 — Transformations")
        pd.DataFrame(
            brd_json["Section 5 — Transformations"],
            columns=["Output Column", "Expression"]
        ).to_excel(writer, sheet_name="5_Transformations", index=False)

        # -------------------------
        # Section 6 — Data Dependencies
        # -------------------------
        logger.info("Writing Section 6 — Data Dependencies")
        dependency_rows = []

        for dep in brd_json["Section 6 — Data Dependencies"]:
            dependency_rows.append({
                "Column": dep.get("Column"),
                "Depends On": ", ".join(dep.get("Depends On", []))
            })

        pd.DataFrame(
            dependency_rows,
            columns=["Column", "Depends On"]
        ).to_excel(writer, sheet_name="6_DataDependencies", index=False)

        # -------------------------
        # Section 7 — BigQuery Requirements Summary
        # -------------------------
        logger.info("Writing Section 7 — BigQuery Requirements Summary")
        summary = brd_json["Section 7 — BigQuery Requirements Summary"]

        # 7a — Tables to Migrate
        pd.DataFrame(
            {"Tables to Migrate": summary.get("Tables to Migrate", [])}
        ).to_excel(writer, sheet_name="7a_BQ_Tables", index=False)

        # 7b — Columns to Migrate
        pd.DataFrame(
            summary.get("Columns to Migrate", []),
            columns=["Table", "Column", "Data Type"]
        ).to_excel(writer, sheet_name="7b_BQ_Columns", index=False)

        # 7c — PK / FK Dependencies
        pd.DataFrame(
            {"PK_FK Dependencies": summary.get(
                "PrimaryKey_ForeignKey Dependencies", []
            )}
        ).to_excel(writer, sheet_name="7c_BQ_PKFK", index=False)

        # 7d — Lookup Tables
        pd.DataFrame(
            {"Lookup Tables": summary.get(
                "Lookup_Reference Tables Needed", []
            )}
        ).to_excel(writer, sheet_name="7d_BQ_Lookups", index=False)

        # 7e — Transformations in BigQuery
        pd.DataFrame(
            {"Transformations": summary.get(
                "Transformations Handled in BigQuery", []
            )}
        ).to_excel(writer, sheet_name="7e_BQ_Transforms", index=False)

    logger.info("BRD Excel created successfully")
