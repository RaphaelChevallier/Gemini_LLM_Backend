import os
from collections import defaultdict

import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')

def execute_generated_sql(sql_query):
    print(sql_query)
    try:
        conn = createConn()
        # Connect to the database
        cur = conn.cursor()
        cur.execute(sql_query)
        generated_sql_results = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        data_as_dicts = []
        for row in generated_sql_results:
            # Combine column names and data as a dictionary
            data_dict = dict(zip(column_names, row))
            data_as_dicts.append(data_dict)
        return data_as_dicts
    except Exception as e:
        return
        # print("Error from executing query:", e)
        # print("The query is: ", sql_query)
    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

def getTableSchema():
    column_comments_query = """
        select
            c.table_name,
        obj_description(format('%s.%s',c.table_schema,c.table_name)::regclass::oid, 'pg_class') as table_comment,
            c.column_name as column,
            pgd.description as column_comment
        from pg_catalog.pg_statio_all_tables as st
        inner join pg_catalog.pg_description pgd on (
            pgd.objoid = st.relid
        )
        inner join information_schema.columns c on (
            pgd.objsubid   = c.ordinal_position and
            c.table_schema = st.schemaname and
            c.table_name   = st.relname
        ) where obj_description(format('%s.%s',c.table_schema,c.table_name)::regclass::oid, 'pg_class') is not null and c.table_name not in ('property', 'avm')
    """
    try:
        conn = createConn()
        # Create a cursor object
        cur = conn.cursor()
        cur2 = conn.cursor()

        # Execute a query
        query = column_comments_query
        cur.execute(query)
        column_comments_result = cur.fetchall()

        visited_table_names = defaultdict(list)
        example_row_dict = defaultdict(list)
        output_dict = {}
        # Iterate through each tuple in the data list
        for row in column_comments_result:
            # Extract table name, comment, and column information
            table_name, table_comment, column_name, column_comment = row

            if table_name not in visited_table_names:
                example_row_dict = defaultdict(list)
                example_rows_query = f"""SELECT *
                    FROM {table_name}
                    WHERE random() < (
                    SELECT (random() * COUNT(*)) / 20
                    FROM {table_name}
                    )
                    LIMIT 20;
                    """
                cur2.execute(example_rows_query)
                example_rows = cur2.fetchall()
                for desc in cur2.description:
                    example_row_dict[desc[0]]
                # print(example_row_dict)
                # Process each row
                for index, key in enumerate(example_row_dict):
                    for row in example_rows:
                        example_row_dict[key].append(row[index])
                visited_table_names[table_name]

            # Create a dictionary for the current column
            column_dict = {
                "column_comment": column_comment,
                # "example_row_values": []  # Initialize an empty list for example values
            }

            # Check if the table already exists in the output dictionary
            if table_name not in output_dict:
            # If not, create a new dictionary for the table
                output_dict[table_name] = {
                "table_comment": table_comment,
                "columns": {}
                }

            # Add the column dictionary to the table's "columns" dictionary
            output_dict[table_name]["columns"][column_name] = column_dict
            # output_dict[table_name]["columns"][column_name]["example_row_values"] = example_row_dict[column_name]
        # print(output_dict)
        return output_dict

    except Exception as e:
        print("Error:", e)
    finally:
    # Close the cursor and connection
        if cur:
            cur.close()
        if cur2:
            cur2.close()
        if conn:
            conn.close()

def createConn():
    conn = psycopg2.connect(host=os.getenv('DB_HOST'), database=os.getenv('DATABASE'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'))
    return conn

def fetchAddressForVectors():
    try:
        conn = createConn()
        # Create a cursor object
        one_line = list()
        line_two = list()
        line_one = list()
        country_subd = list()
        postal_code = list()
        locality = list()
        county = list()
        cur = conn.cursor()
        query_one_line = """SELECT distinct(one_line), attom_id FROM address where one_line is not null;"""
        query_line2 = """SELECT distinct(line2), attom_id FROM address where line2 is not null;"""
        query_line1 = """SELECT distinct(line1), attom_id FROM address where line1 is not null;"""
        query_country_subd = """SELECT distinct(country_subd), attom_id FROM address where country_subd is not null;"""
        query_postal_code = """SELECT distinct(postal1), attom_id FROM address where postal1 is not null;"""
        query_locality = """SELECT distinct(locality), attom_id FROM address where locality is not null;"""
        query_county = """SELECT distinct(county), attom_id FROM address where county is not null;"""
        cur.execute(query_line1)
        line1_results = cur.fetchall()
        for row in line1_results:
            line_one.append(row)

        cur.execute(query_postal_code)
        postal_code_results = cur.fetchall()
        for row in postal_code_results:
            postal_code.append(row)

        cur.execute(query_locality)
        locality_results = cur.fetchall()
        for row in locality_results:
            locality.append(row)

        cur.execute(query_county)
        county_results = cur.fetchall()
        for row in county_results:
            county.append(row)

        cur.execute(query_country_subd)
        country_subd_results = cur.fetchall()
        for row in country_subd_results:
            country_subd.append(row)

        cur.execute(query_one_line)
        one_line_results = cur.fetchall()
        for row in one_line_results:
            one_line.append(row)

        cur.execute(query_line2)
        line_two_results = cur.fetchall()
        for row in line_two_results:
            line_two.append(row)
        return one_line, line_two, line_one, county, country_subd, postal_code, locality
        # combine = one_line + line_two + county + locality + country_subd + postal_code + line_one
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()