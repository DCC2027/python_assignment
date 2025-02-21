import pandas as pd
import sqlite3

# read csv as dataframe
train_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/train.csv")
test_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/test.csv")
ideal_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/ideal.csv")

# connect to SQLite database
conn = sqlite3.connect("/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
cursor = conn.cursor()

# create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS train_data (
    X REAL PRIMARY KEY,
    Y1 REAL,
    Y2 REAL,
    Y3 REAL,
    Y4 REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS test_data (
    X REAL PRIMARY KEY,
    Y REAL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ideal_functions (
    X REAL PRIMARY KEY,
    """ + ", ".join([f"Y{i+1} REAL" for i in range(50)]) + """
);
""")

# save dataframes into dataset
train_df.to_sql("train_data", conn, if_exists="replace", index=False)
test_df.to_sql("test_data", conn, if_exists="replace", index=False)
ideal_df.to_sql("ideal_functions", conn, if_exists="replace", index=False)

print("Data loading completed!")


def dump_unit_test():
    """ unit test: sanity check, whether data dumped into database and consistent with original csv file
    """
    print("===============performing unit test================")
    train_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/train.csv")
    cursor.execute("SELECT * FROM train_data LIMIT 1;")
    row = cursor.fetchone()
    expected_row = train_df.iloc[0]  
    sanity_check = True
    for i in range(len(row)):
        if row[i] != expected_row.iloc[i]:
            sanity_check == False
            break

    if not sanity_check:
        print("train_df unit test failed. Program exit.")
        exit()
    
    test_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/test.csv")
    cursor.execute("SELECT * FROM test_data LIMIT 1;")
    row = cursor.fetchone()
    expected_row = test_df.iloc[0]  
    sanity_check = True
    for i in range(len(row)):
        if row[i] != expected_row.iloc[i]:
            sanity_check == False
            break

    if not sanity_check:
        print("test_data unit test failed. Program exit.")
        exit()

    ideal_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/ideal.csv")
    cursor.execute("SELECT * FROM ideal_functions LIMIT 1;")
    row = cursor.fetchone()
    expected_row = ideal_df.iloc[0]  
    sanity_check = True
    for i in range(len(row)):
        if row[i] != expected_row.iloc[i]:
            sanity_check == False
            break

    if not sanity_check:
        print("ideal_df unit test failed. Program exit.")
        exit()

    else:
        print("unit test passed!")

    print("===================================================")
    
dump_unit_test()


conn.close()