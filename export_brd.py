import pandas as pd

def export_to_excel(brd_json, filename="BRD_Output.xlsx"):
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:

        # -------------------------
        # Section 1 — Tables Needed
        # -------------------------
        pd.DataFrame({"Tables Needed": brd_json.get("Section 1 — Tables Needed", [])}) \
            .to_excel(writer, sheet_name="1_Tables", index=False)

        # -------------------------
        # Section 2 — Columns Needed
        # -------------------------
        pd.DataFrame({"Columns Needed": brd_json.get("Section 2 — Columns Needed", [])}) \
            .to_excel(writer, sheet_name="2_Columns", index=False)

        # -------------------------
        # Section 3 — Joins
        # -------------------------
        joins = brd_json.get("Section 3 — Joins", [])
        if isinstance(joins, list):
            pd.DataFrame(joins).to_excel(writer, sheet_name="3_Joins", index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name="3_Joins")

        # -------------------------
        # Section 4 — Filters
        # -------------------------
        filters = brd_json.get("Section 4 — Filters", [])
        if isinstance(filters, list):
            pd.DataFrame(filters).to_excel(writer, sheet_name="4_Filters", index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name="4_Filters")

        # -------------------------
        # Section 5 — Transformations
        # -------------------------
        transformations = brd_json.get("Section 5 — Transformations", [])
        if isinstance(transformations, list):
            pd.DataFrame(transformations).to_excel(writer, sheet_name="5_Transformations", index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name="5_Transformations")

        # -------------------------
        # Section 6 — Data Dependencies
        # -------------------------
        dependencies = brd_json.get("Section 6 — Data Dependencies", [])
        if isinstance(dependencies, list):
            pd.DataFrame(dependencies).to_excel(writer, sheet_name="6_DataDependencies", index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name="6_DataDependencies")

        # -------------------------
        # Section 7 — BigQuery Requirements Summary
        # -------------------------
        summary = brd_json.get("Section 7 — BigQuery Requirements Summary", {})
        if isinstance(summary, dict):
            # Flatten BigQuery summary into multiple sheets
            pd.DataFrame({"Tables to Migrate": summary.get("Tables to Migrate", [])}) \
                .to_excel(writer, sheet_name="7a_BQ_Tables", index=False)

            pd.DataFrame(summary.get("Columns to Migrate", [])) \
                .to_excel(writer, sheet_name="7b_BQ_Columns", index=False)

            pd.DataFrame({"PK_FK Dependencies": summary.get("PrimaryKey_ForeignKey Dependencies", [])}) \
                .to_excel(writer, sheet_name="7c_BQ_PKFK", index=False)

            pd.DataFrame({"Lookup Tables": summary.get("Lookup_Reference Tables Needed", [])}) \
                .to_excel(writer, sheet_name="7d_BQ_Lookups", index=False)

            pd.DataFrame({"Transformations": summary.get("Transformations Handled in BigQuery", [])}) \
                .to_excel(writer, sheet_name="7e_BQ_Transforms", index=False)

        print("BRD Excel created successfully!")
