import sqlite3
import pandas as pd
import numpy as np
from loader import *

class Trainer():
    """
    Trainer class for finding the best matching ideal functions for training data
    """
    def __init__(self, db_connector, train_loader, function_loader):
        """
        Initialize the Trainer with database connector and data loaders

        Args::
        db_connector: Database connection instance.
        train_loader: Data loader for training data.
        function_loader: Data loader for ideal functions.
        """       
        self.db = db_connector
        self.train_loader = train_loader
        self.function_loader = function_loader
        

    def train(self,):
        """
        Perform training by finding the best matching ideal function for each training dataset column

        Returns:
        dict: A dictionary mapping each training function to its best matching ideal function
        """
        best_functions = {}

        for y_train_col in ["y1", "y2", "y3", "y4"]:
            min_sse = float('inf')  
            best_function = None

            for y_ideal_col in [f"y{i+1}" for i in range(50)]:
                sse = np.sum((self.train_loader.df[y_train_col] - self.function_loader.df[y_ideal_col]) ** 2)

                if sse < min_sse:
                    min_sse = sse
                    best_function = y_ideal_col

            best_functions[y_train_col] = best_function
            print(f"Training function: {y_train_col} the best matched function is {best_function}, SSE = {min_sse:.6f}")
        return best_functions

    def dump_ideal(self, best_functions):
        """
        Save the best function mappings into the database

        Args:
        best_functions (dict): Dictionary mapping training functions to ideal functions.
        """
        self.db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS best_function_mapping (
            train_function TEXT PRIMARY KEY,
            ideal_function TEXT
        );
        """)

        self.db.cursor.execute("DELETE FROM best_function_mapping")

        for train_func, ideal_func in best_functions.items():
            self.db.cursor.execute("INSERT INTO best_function_mapping (train_function, ideal_function) VALUES (?, ?)", (train_func, ideal_func))

        self.db.conn.commit()
        self.db.conn.close()

        print("Best matched funcs save in dataset！")

def main():
    """
    Main function to execute the training process
    """
    print("================performing training=================")
    db_connector =DBConnector(db_path="/Users/lincong/Desktop/python_course/assignment/Dataset/functions.db")
    train_loader = TrainDataloader(db_connector)
    function_loader =FunctionDataloader(db_connector)

    trainer = Trainer(db_connector, train_loader, function_loader)
    best_functions = trainer.train()
    trainer.dump_ideal(best_functions)

def train_unit_test():
    """
    Perform a unit test to validate the training function
    """
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

def teams_others_update():
    print("other team member's update")

train_unit_test()

main()