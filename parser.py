# parser.py
import logging
import sqlglot
from sqlglot.expressions import Column

logger = logging.getLogger(__name__)


def analyze_sql(sql_text: str) -> dict:
    """
    Parses SQL text using SQLGlot and extracts
    basic structural information for analysis.
    """

    logger.info("Parsing SQL")
    parsed = sqlglot.parse_one(sql_text)

    # -------------------------
    # Extract tables
    # -------------------------
    tables = [t.name for t in parsed.find_all(sqlglot.exp.Table)]
    logger.debug(f"Tables found: {tables}")

    # -------------------------
    # Extract selected columns
    # -------------------------
    select_columns = [
        col.alias_or_name
        for col in parsed.selects
        if isinstance(col, Column)
    ]
    logger.debug(f"Selected columns: {select_columns}")

    # -------------------------
    # Extract WHERE clause
    # -------------------------
    where_clause = parsed.args.get("where")
    where_clause_str = str(where_clause) if where_clause else None

    # -------------------------
    # Extract JOIN conditions
    # -------------------------
    joins = parsed.find_all(sqlglot.exp.Join)
    join_conditions = [
        str(j.args.get("on"))
        for j in joins
        if j.args.get("on") is not None
    ]
    logger.debug(f"Join conditions: {join_conditions}")

    # -------------------------
    # Extract GROUP BY
    # -------------------------
    group_by = parsed.args.get("group")
    group_by_str = str(group_by) if group_by else None

    parsed_sql = {
        "tables": tables,
        "select_columns": select_columns,
        "where": where_clause_str,
        "joins": join_conditions,
        "group_by": group_by_str
    }

    # -------------------------
    # Extract tables with aliases (SQLGlot-safe)
    # -------------------------
    tables = []
    table_alias_map = []

    for t in parsed.find_all(sqlglot.exp.Table):
        table_name = t.name
        alias_name = None

        if t.alias:
            # Case 1: alias is a string
            if isinstance(t.alias, str):
                alias_name = t.alias

            # Case 2: alias is an Alias expression
            elif hasattr(t.alias, "this") and t.alias.this is not None:
                alias_name = str(t.alias.this)

        tables.append(table_name)
        table_alias_map.append({
            "Table": table_name,
            "Alias": alias_name
        })

    logger.debug(f"Table alias mapping: {table_alias_map}")



# -------------------------
# Local test run
# -------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with open("sample.sql") as f:
        sql_text = f.read()

    result = analyze_sql(sql_text)
    print(result)
