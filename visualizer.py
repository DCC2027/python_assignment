import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import *
from test import *
from train import *


### **误差分析类**
class ErrorAnalyzer:
    def __init__(self, test_mapping_df):
        self.test_mapping_df = test_mapping_df

    def compute_statistics(self):
        """计算误差统计"""
        delta_y = self.test_mapping_df["Delta_Y"]
        stats = {
            "mean_error": np.mean(delta_y),
            "max_error": np.max(delta_y),
            "std_dev": np.std(delta_y),
            "matched_points": len(self.test_mapping_df)
        }
        return stats

    def save_results(self, filename="test_mapping_results.csv"):
        """将匹配数据保存到 CSV"""
        self.test_mapping_df.to_csv(filename, index=False)
        print(f"数据已保存为 {filename}")


### **绘图类**
class Plotter:
    def __init__(self, test_mapping_df, ideal_df):
        self.test_mapping_df = test_mapping_df
        self.ideal_df = ideal_df

    # def plot_error_histogram(self):
    #     """绘制误差直方图"""
    #     delta_y = self.test_mapping_df["Delta_Y"]
    #     plt.figure(figsize=(8, 6))
    #     plt.hist(delta_y, bins=20, color="blue", alpha=0.7)
    #     plt.xlabel("Deviation Delta_Y")
    #     plt.ylabel("Quantity")
    #     plt.title("Deviation Distribution")
    #     plt.show()

    def plot_test_vs_ideal(self, unmatched_test_df):
        """绘制测试数据 vs. 匹配理想函数"""
        x_vals = self.test_mapping_df["X"].values
        y_test_vals = self.test_mapping_df["Y"].values
        ideal_functions = self.test_mapping_df["Ideal_Function"].values
        x_vals_unmatch = unmatched_test_df["X"].values
        y_vals_unmatch = unmatched_test_df["Y_test"].values

        # 查找对应 Y_ideal
        y_ideal_vals = []
        for x, ideal_func in zip(x_vals, ideal_functions):
            ideal_y = self.ideal_df.loc[self.ideal_df["x"] == x, ideal_func].values
            y_ideal_vals.append(ideal_y[0] if len(ideal_y) > 0 else None)

        plt.figure(figsize=(8, 6))
        plt.scatter(x_vals, y_test_vals, c="red", s=10, label="Test Data", alpha=0.7)
        plt.scatter(x_vals, y_ideal_vals, c="green", s=10, label="Matched Ideal Function", alpha=0.7)
        plt.scatter(x_vals_unmatch, y_vals_unmatch, c="gray", s=10, label="Unmatched X", alpha=0.7)
        plt.yticks(np.arange(-40, 40, 5))
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.title("Test Data vs. Ideal Function Matching")
        plt.show()


### **可视化管理类**
class Visualizer:
    def __init__(self, db_connector):
        self.db = db_connector
        self.test_mapping_df = pd.read_sql("SELECT * FROM test_mapping", self.db.conn)
        self.ideal_df = pd.read_sql("SELECT * FROM ideal_functions", self.db.conn)

        self.analyzer = ErrorAnalyzer(self.test_mapping_df)
        self.plotter = Plotter(self.test_mapping_df, self.ideal_df)

        print("读取存储的匹配数据", self.test_mapping_df.head(10))

    def run(self, unmatched_test_df):
        """运行可视化流程"""
        stats = self.analyzer.compute_statistics()
        print(f"平均误差: {stats['mean_error']:.6f}")
        print(f"最大误差: {stats['max_error']:.6f}")
        print(f"误差标准差: {stats['std_dev']:.6f}")
        print(f"匹配到的测试点总数: {stats['matched_points']}")

        self.analyzer.save_results()
        # self.plotter.plot_error_histogram()
        self.plotter.plot_test_vs_ideal(unmatched_test_df)



def main():
    db_connector = DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")

    # 先创建 TrainDataloader 和 FunctionDataloader
    train_loader = TrainDataloader(db_connector)
    function_loader = FunctionDataloader(db_connector)

    # 传入 train_loader 和 function_loader  
    tester = Tester(db_connector, train_loader, function_loader, match_thresh=np.sqrt(2))
    matched_test_data, unmatched_test_data = tester.run()

    # **运行可视化**
    visualizer = Visualizer(db_connector)
    visualizer.run(pd.DataFrame(unmatched_test_data, columns=["X", "Y_test", "Delta_Y", "Ideal_Function", "Y_ideal"]))

    db_connector.conn.close()

main()

#X, Y, Delta_Y, Ideal_Function, Y_ideal