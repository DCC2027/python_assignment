import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import *
from test import *
from train import *


class ErrorAnalyzer:
    """
    Class for analyzing errors in test data matching.
    """
    def __init__(self, test_mapping_df):
        """
        Initialize the ErrorAnalyzer with the test mapping DataFrame.

        Parameters:
        test_mapping_df (DataFrame): DataFrame containing test data and their corresponding matches.
        """
        self.test_mapping_df = test_mapping_df

    def compute_statistics(self):
        """
        Compute error statistics.

        Returns:
        dict: Dictionary containing mean error, max error, standard deviation, and count of matched points.
        """
        delta_y = self.test_mapping_df["Delta_Y"]
        stats = {
            "mean_error": np.mean(delta_y),
            "max_error": np.max(delta_y),
            "std_dev": np.std(delta_y),
            "matched_points": len(self.test_mapping_df)
        }
        return stats

    def save_results(self, filename="test_mapping_results.csv"):
        """
        Save the matched data to a CSV file.

        Parameters:
        filename (str): The name of the file to save the results to. Defaults to "test_mapping_results.csv".
        """
        self.test_mapping_df.to_csv(filename, index=False)
        print(f"Data saved as {filename}")


class Plotter:
    """
    Class for plotting test data against ideal functions.
    """
    def __init__(self, test_mapping_df, ideal_df):
        """
        Initialize the Plotter with test mapping and ideal function DataFrames.

        Parameters:
        test_mapping_df (DataFrame): DataFrame containing test data and their corresponding matches.
        ideal_df (DataFrame): DataFrame containing ideal function data.
        """
        self.test_mapping_df = test_mapping_df
        self.ideal_df = ideal_df

    def plot_test_vs_ideal(self, unmatched_test_df):
        """
        Plot test data versus matched ideal functions.

        Parameters:
        unmatched_test_df (DataFrame): DataFrame containing unmatched test data.
        """
        x_vals = self.test_mapping_df["X"].values
        y_test_vals = self.test_mapping_df["Y"].values
        x_vals_unmatch = unmatched_test_df["X"].values
        y_vals_unmatch = unmatched_test_df["Y_test"].values
        y_ideal_vals = self.test_mapping_df["Best_ideal_y"].values


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


class Visualizer:
    """
    Class to manage the visualization process.
    """
    def __init__(self, db_connector):
        """
        Initialize the Visualizer with a database connector.

        Parameters:
        db_connector: Database connection instance.
        """
        self.db = db_connector
        try:
            self.test_mapping_df = pd.read_sql("SELECT * FROM test_mapping", self.db.conn)
            self.ideal_df = pd.read_sql("SELECT * FROM ideal_functions", self.db.conn)
        except Exception as e:
            raise DataLoadingError(f"Failed to load data in visualizer: {e}")
        
        self.analyzer = ErrorAnalyzer(self.test_mapping_df)
        self.plotter = Plotter(self.test_mapping_df, self.ideal_df)

        print("Loaded stored matching data", self.test_mapping_df.head(10))

    def run(self, unmatched_test_df):
        """
        Execute the visualization process.

        Parameters:
        unmatched_test_df (DataFrame): DataFrame containing unmatched test data.
        """
        stats = self.analyzer.compute_statistics()
        print(f"Mean error: {stats['mean_error']:.6f}")
        print(f"Max error: {stats['max_error']:.6f}")
        print(f"Standard deviation of error: {stats['std_dev']:.6f}")
        print(f"Total number of matched test points: {stats['matched_points']}")

        self.analyzer.save_results()
        self.plotter.plot_test_vs_ideal(unmatched_test_df)



def main():
    db_connector = DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")

    train_loader = TrainDataloader(db_connector)
    train_loader.viz_df()
    function_loader = FunctionDataloader(db_connector)
    function_loader.viz_df()
    test_loader = TestDataloader(db_connector)
    test_loader.viz_df()
  
    tester = Tester(db_connector, train_loader, function_loader, test_loader, match_thresh=np.sqrt(2))
    matched_test_data, unmatched_test_data = tester.run()

    visualizer = Visualizer(db_connector)
    visualizer.run(pd.DataFrame(unmatched_test_data, columns=["X", "Y_test", "Delta_Y", "Ideal_Function", "Y_ideal"]))

    db_connector.conn.close()

main()