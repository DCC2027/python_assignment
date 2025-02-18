import pandas as pd
import sqlite3

# 读取 CSV 文件
train_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/train.csv")
test_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/test.csv")
ideal_df = pd.read_csv("/Users/lincong/Desktop/python_course/assignment/Dataset/ideal.csv")

# 连接 SQLite 数据库
conn = sqlite3.connect("/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
cursor = conn.cursor()

# 创建表
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

# 存入数据库
train_df.to_sql("train_data", conn, if_exists="replace", index=False)
test_df.to_sql("test_data", conn, if_exists="replace", index=False)
ideal_df.to_sql("ideal_functions", conn, if_exists="replace", index=False)



# 关闭连接
conn.close()
print("数据加载完成！")
