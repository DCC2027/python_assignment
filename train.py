import sqlite3
import pandas as pd
import numpy as np
from loader import *

class Trainer():
    def __init__(self, db_connector, train_loader, function_loader):
        self.db = db_connector
        self.train_loader = train_loader
        self.function_loader = function_loader
        # 连接数据库

    def train(self,):
        # 存储最优匹配的理想函数
        best_functions = {}

        # 遍历训练数据的 4 个 Y 列
        for y_train_col in ["y1", "y2", "y3", "y4"]:
            min_sse = float('inf')  # 设定初始最小误差为无穷大
            best_function = None

            # 遍历 50 个理想函数
            for y_ideal_col in [f"y{i+1}" for i in range(50)]:
                # 计算 SSE（只对相同 X 的数据计算）
                sse = np.sum((self.train_loader.df[y_train_col] - self.function_loader.df[y_ideal_col]) ** 2)

                # 选择误差最小的理想函数
                if sse < min_sse:
                    min_sse = sse
                    best_function = y_ideal_col

            # 记录当前训练数据对应的最优理想函数
            best_functions[y_train_col] = best_function
            print(f"Training function: {y_train_col} the best matched function is {best_function}, SSE = {min_sse:.6f}")
        return best_functions

    def dump_ideal(self, best_functions):
        # 创建匹配表（如果不存在）
        self.db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS best_function_mapping (
            train_function TEXT PRIMARY KEY,
            ideal_function TEXT
        );
        """)

        # 清空旧数据
        self.db.cursor.execute("DELETE FROM best_function_mapping")

        # 插入新的最佳匹配数据
        for train_func, ideal_func in best_functions.items():
            self.db.cursor.execute("INSERT INTO best_function_mapping (train_function, ideal_function) VALUES (?, ?)", (train_func, ideal_func))

        # 提交 & 关闭
        self.db.conn.commit()
        self.db.conn.close()

        print("Best matched funcs save in dataset！")

def main():
    print("================performing training=================")
    db_connector =DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
    train_loader = TrainDataloader(db_connector)
    function_loader =FunctionDataloader(db_connector)

    trainer = Trainer(db_connector, train_loader, function_loader)
    best_functions = trainer.train()
    trainer.dump_ideal(best_functions)

def train_unit_test():
    print("===============performing unit test================")
    db_connector =DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
    fake_train_loader = FunctionDataloader(db_connector)
    function_loader =FunctionDataloader(db_connector)
    
    expected_func = {'y1': 'y1', 'y2': 'y2', 'y3': 'y3', 'y4': 'y4'}

    
    trainer = Trainer(db_connector, fake_train_loader, function_loader)
    best_functions = trainer.train()

    sanity_check = True
    for key, value in expected_func.items():
        if best_functions[key] != expected_func[key]:
            sanity_check = False
            break

    if sanity_check:
        print("unit test passed!")
    else:
        print("unit test failed. Program exit.")
        exit(0)
    print("====================================================")


train_unit_test()

main()