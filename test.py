import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import *

### **测试数据匹配类**
class Tester:
    def __init__(self, db_connector, train_loader, function_loader, match_thresh=np.sqrt(2)):
        self.db = db_connector
        self.train_loader = train_loader
        self.function_loader = function_loader  
        self.threshold_factor =  match_thresh

        # # 读取数据库中的数据
        # self.test_df = pd.read_sql("SELECT * FROM test_data", self.db.conn)
        # self.ideal_df = pd.read_sql("SELECT * FROM ideal_functions", self.db.conn)
        # self.train_df = pd.read_sql("SELECT * FROM train_data", self.db.conn)
        self.best_functions = pd.read_sql("SELECT * FROM best_function_mapping", self.db.conn)

        print("测试数据读取完成！")
        print("最佳匹配表:", self.best_functions)

    def calculate_max_deviation(self):
        """计算训练数据和最佳理想函数之间的最大误差"""
        max_deviation = {}



        for _, row in self.best_functions.iterrows():
            train_func = row["train_function"]
            ideal_func = row["ideal_function"]

            deviation = abs(self.train_loader.df[train_func] - self.function_loader.df[ideal_func])
            max_deviation[ideal_func] = deviation.max()

        print("训练数据和最佳理想函数的最大误差:", max_deviation)
        return max_deviation
    
         # 存储最大误差
        

    def match_test_data(self):
        max_deviation = self.calculate_max_deviation()
        """匹配测试数据"""
        matched_test_data = []
        unmatched_test_data = []
        self.test_df = pd.read_sql("SELECT * FROM test_data", self.db.conn)
        


        for _, test_row in self.test_df.iterrows():
            x_test, y_test = test_row["x"], test_row["y"]
            best_match = None
            best_deviation = float("inf")

            for _, row in self.best_functions.iterrows():
                ideal_func = row["ideal_function"]
                ideal_y = self.function_loader.df.loc[self.function_loader.df["x"] == x_test, ideal_func].values

                if len(ideal_y) > 0:
                    deviation = abs(y_test - ideal_y[0])

                    if deviation <= self.threshold_factor * max_deviation[ideal_func]:
                        if deviation < best_deviation:
                            best_deviation = deviation
                            best_match = ideal_func

            if best_match:
                matched_test_data.append((x_test, y_test, best_deviation, best_match, ideal_y[0]))
            else:
                unmatched_test_data.append((x_test, y_test, best_deviation, None, None))

        print("测试数据匹配完成！")
        print("最终匹配结果:", matched_test_data[:10])  # 仅打印前 10 行

        return matched_test_data, unmatched_test_data

    def save_matched_data(self, matched_test_data):
   
        cursor = self.db.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_mapping")  # ✅ 先删除旧表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_mapping (
            X REAL,
            Y REAL,          
            Delta_Y REAL,
            Ideal_Function TEXT,
            Y_ideal REAL
        );
        """)

        cursor.executemany(
            "INSERT INTO test_mapping (X, Y, Delta_Y, Ideal_Function, Y_ideal) VALUES (?, ?, ?, ?, ?)",
            matched_test_data
        )

        self.db.conn.commit()
        print("测试数据匹配结果已存入数据库！")

    def run(self):
        """运行匹配流程"""
        matched_test_data, unmatched_test_data = self.match_test_data()
        self.save_matched_data(matched_test_data)

        return matched_test_data, unmatched_test_data
    
def main():
    db_connector =DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
    train_loader = TrainDataloader(db_connector)
    function_loader =FunctionDataloader(db_connector)
    
    tester = Tester(db_connector, train_loader, function_loader)
    tester.run()

main()
