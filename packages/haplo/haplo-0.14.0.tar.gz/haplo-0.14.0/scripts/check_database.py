import pandas as pd
import sqlite3

def check_640m():
    # Read sqlite query results into a pandas DataFrame
    # con = sqlite3.connect("data/640m_parameters_and_phase_amplitudes.db")
    sqliteConnection = sqlite3.connect("data_nobackup/640m_parameters_and_phase_amplitudes.db")
    sql_query = """SELECT name FROM sqlite_master 
       WHERE type='table';"""

    # Creating cursor object using connection object
    cursor = sqliteConnection.cursor()

    # executing our sql query
    cursor.execute(sql_query)
    print("List of tables\n")

    # printing all tables list
    print(cursor.fetchall())

    cursor.execute("SELECT COUNT(*) FROM main")
    result = cursor.fetchone()[0]
    print(result)

    # Execute the PRAGMA integrity_check command
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchall()
    print(result)




    #  df = pd.read_sql_query("SELECT *", con)

    # Verify that result of SQL query is stored in the dataframe
    #  print(df)
    # print(len(df))

    sqliteConnection.close()

if __name__ == '__main__':
    check_640m()