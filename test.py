import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loader import *

class Tester:
    """_Tester class for matching test data with the best ideal functions
    """
    def __init__(self, db_connector, train_loader, function_loader, test_loader, match_thresh=np.sqrt(2)):
        self.db = db_connector
        self.train_loader = train_loader
        self.function_loader = function_loader
        self.test_loader = test_loader
        self.threshold_factor =  match_thresh
        try:
            self.best_functions = pd.read_sql("SELECT * FROM best_function_mapping", self.db.conn)
        except Exception as e:
            raise DataLoadingError(f"Failed to load data from table best_function_mapping: {e}")

        print("Test data loaded successfully!")
        print("Best function mappings:", self.best_functions)

    def calculate_max_deviation(self):
        """Calculate the maximum deviation between training data and the best ideal functions

        Returns:
        dict: Dictionary containing the maximum deviation for each ideal function
        """
        max_deviation = {}



        for _, row in self.best_functions.iterrows():
            train_func = row["train_function"]
            ideal_func = row["ideal_function"]

            deviation = abs(self.train_loader.df[train_func] - self.function_loader.df[ideal_func])
            max_deviation[ideal_func] = deviation.max()

        print("Maximum deviation between training and ideal functions:", max_deviation)
        return max_deviation


    def match_test_data(self):
        """
        Match test data against the best ideal functions based on deviation threshold

        Returns:
        tuple: Matched and unmatched test data
        """
        max_deviation = self.calculate_max_deviation()
        matched_test_data = []
        unmatched_test_data = []

        for _, test_row in self.test_loader.df.iterrows():
            x_test, y_test = test_row["x"], test_row["y"]
            best_match = None
            best_deviation = float("inf")
            best_ideal_y = None  

            for _, row in self.best_functions.iterrows():
                ideal_func = row["ideal_function"]
                ideal_y_candidates = self.function_loader.df.loc[self.function_loader.df["x"] == x_test, ideal_func].values

                if len(ideal_y_candidates) > 0:  
                    for ideal_y in ideal_y_candidates: 
                        deviation = abs(y_test - ideal_y)
                        
                        if deviation <= self.threshold_factor * max_deviation[ideal_func]:
                            if deviation < best_deviation:
                                best_deviation = deviation
                                best_match = ideal_func
                                best_ideal_y = ideal_y  

            if best_match:
                matched_test_data.append((x_test, y_test, best_deviation, best_match, best_ideal_y))
            else:
                unmatched_test_data.append((x_test, y_test, best_deviation, None, None))

        print("Test data matching completed!")
        print("Final matching results (first 10 entries):", matched_test_data[:10])  

        return matched_test_data, unmatched_test_data


    def save_matched_data(self, matched_test_data):
        """
        Save matched test data into the database

        Parameters:
        matched_test_data (list): List of matched test data tuples.
        """
        cursor = self.db.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_mapping") 
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
        print("Matched test data saved in the database!")

    def run(self):
        """
        Execute the test data matching process

        Returns:
        tuple: Matched and unmatched test data.
        """
        matched_test_data, unmatched_test_data = self.match_test_data()
        self.save_matched_data(matched_test_data)

        return matched_test_data, unmatched_test_data
    


def test_unit_test(tester):
    """
    Perform a unit test to verify test data matching
    """
    print("===============performing test test================")
    matched_test_data, unmatched_test_data = tester.match_test_data()
    
    total_matched = len(matched_test_data)
    total_unmatched = len(unmatched_test_data)
    total_test_cases = len(tester.test_loader.df)

    assert total_matched + total_unmatched == total_test_cases, (
        f"test data count: 匹配 {total_matched} + 未匹配 {total_unmatched} ≠ 总测试 {total_test_cases}"
    )

    print("total_matched :" , total_matched)
    print("total_unmatched :" , total_unmatched)
    print("total_test_cases :" , total_test_cases)
    print("Test passed: Matched + Unmatched = Total test cases")
    
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

