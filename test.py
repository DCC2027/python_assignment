import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import *

### **测试数据匹配类**
class Tester:
    def __init__(self, db_connector, train_loader, function_loader, test_loader, match_thresh=np.sqrt(2)):
        self.db = db_connector
        self.train_loader = train_loader
        self.function_loader = function_loader
        self.test_loader = test_loader
        self.threshold_factor =  match_thresh

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


        for _, test_row in self.test_loader.df.iterrows():
            x_test, y_test = test_row["x"], test_row["y"]
            best_match = None
            best_deviation = float("inf")
            best_ideal_y = None  # 用于存储最佳 Y_ideal 值

            for _, row in self.best_functions.iterrows():
                ideal_func = row["ideal_function"]
                ideal_y_candidates = self.function_loader.df.loc[self.function_loader.df["x"] == x_test, ideal_func].values

                if len(ideal_y_candidates) > 0:  # 确保找到了匹配
                    for ideal_y in ideal_y_candidates:  # 遍历所有可能的 Y_ideal 值
                        deviation = abs(y_test - ideal_y)
                        
                        if deviation <= self.threshold_factor * max_deviation[ideal_func]:
                            if deviation < best_deviation:
                                best_deviation = deviation
                                best_match = ideal_func
                                best_ideal_y = ideal_y  # 记录当前误差最小的 Y_ideal

            if best_match:
                matched_test_data.append((x_test, y_test, best_deviation, best_match, best_ideal_y))
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
            Best_ideal_y REAL
        );
        """)

        cursor.executemany(
            "INSERT INTO test_mapping (X, Y, Delta_Y, Ideal_Function, Best_ideal_y) VALUES (?, ?, ?, ?, ?)",
            matched_test_data
        )

        self.db.conn.commit()
        print("测试数据匹配结果已存入数据库！")

    def run(self):
        """运行匹配流程"""
        matched_test_data, unmatched_test_data = self.match_test_data()
        self.save_matched_data(matched_test_data)

        return matched_test_data, unmatched_test_data
    




def test_unit_test(tester):
    print("===============performing test test================")
    """测试 matched 和 unmatched 数量总和是否等于 test.csv 中的 X 数量"""
    matched_test_data, unmatched_test_data = tester.match_test_data()
    
    total_matched = len(matched_test_data)
    total_unmatched = len(unmatched_test_data)
    total_test_cases = len(tester.test_loader.df)

    # 直接使用 assert 进行检查
    assert total_matched + total_unmatched == total_test_cases, (
        f"匹配数据数量错误: 匹配 {total_matched} + 未匹配 {total_unmatched} ≠ 总测试 {total_test_cases}"
    )

    print("total_matched :" , total_matched)
    print("total_unmatched :" , total_unmatched)
    print("total_test_cases :" , total_test_cases)
    print("✅ 测试通过: 匹配 + 未匹配 = 测试数据总数")
    
    print("================================================")

def main():
    db_connector =DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
    train_loader = TrainDataloader(db_connector)
    function_loader =FunctionDataloader(db_connector)
    test_loader = TestDataloader(db_connector)
    
    tester = Tester(db_connector, train_loader, function_loader, test_loader)
    tester.run()

    test_unit_test(tester) 

main()

