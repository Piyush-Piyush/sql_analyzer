import sqlglot
from sqlglot.expressions import Column

def analyze_sql(sql_text):
    parsed = sqlglot.parse_one(sql_text)

    # --- Extract tables ---
    tables = [table.name for table in parsed.find_all(sqlglot.exp.Table)]

    # --- Extract selected columns ---
    select_columns = [
        col.alias_or_name for col in parsed.selects
        if isinstance(col, Column) or col.name
    ]

    # --- Extract where clause ---
    where_clause = parsed.args.get("where")

    # --- Extract joins ---
    joins = parsed.find_all(sqlglot.exp.Join)
    join_conditions = [join.args.get("on") for join in joins]

    # --- Extract group by ---
    group_by = parsed.args.get("group")

    parsedSql = {
        "tables": tables,
        "select_columns": select_columns,
        "where": str(where_clause) if where_clause else None,
        "joins": [str(j) for j in join_conditions],
        "group_by": str(group_by) if group_by else None
    }
    return parsedSql


# Test run
if __name__ == "__main__":
    sql_text = open("sample.sql").read()
    result = analyze_sql(sql_text)
    print(result)
